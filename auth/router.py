import json
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import timedelta
from jose import jwt, JWTError
from datetime import datetime
from sqlalchemy import update
from pydantic import ValidationError
from authlib.integrations.starlette_client import OAuth

from db.pg_connection import get_db
from config.settings import settings
from auth.models import User, RefreshToken, AuthType
from auth.schemas import UserCreate, UserRead, Token
from auth.utils import get_password_hash, authenticate_user, send_email_verification, send_forgot_password_email
from auth.dependencies import get_current_user, get_redis_client
from utils.custom_logger import logger
from db.redis_connection import RedisClient
from utils.serializers import ResponseData
from RBAC.utils import add_user_to_organization


router = APIRouter(prefix="/auth")

@router.get('/microsoft', tags=["Authentication"])
async def microsoft_login(request: Request):
    if not settings.oauth_microsoft:
        settings.oauth_microsoft = OAuth()
        
        settings.oauth_microsoft.register(
            name='microsoft',
            client_id=settings.microsoft_client_id,
            client_secret=settings.microsoft_client_secret,
            server_metadata_url='https://login.microsoftonline.com/common/v2.0/.well-known/openid-configuration',
            client_kwargs={
                'scope': 'openid email profile',
            }
        )
    
    redirect_uri = request.url_for('microsoft_auth_callback')
    return await settings.oauth_microsoft.microsoft.authorize_redirect(request, redirect_uri)

@router.get('/google', tags=["Authentication"])
async def google_login(request: Request):
    if not settings.oauth_google:
        settings.oauth_google = OAuth()
        
        settings.oauth_google.register(
            name='google',
            client_id=settings.google_client_id,
            client_secret=settings.google_client_secret,
            server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
            client_kwargs={
                'scope': 'email openid profile',
            }
        )
    
    redirect_uri = request.url_for('google_auth_callback')
    return await settings.oauth_google.google.authorize_redirect(request, redirect_uri)


@router.get('/github', tags=["Authentication"])
async def github_login(request: Request):
    """Redirects user to GitHub for authentication."""
    if not settings.oauth_github:
        settings.oauth_github = OAuth()
        settings.oauth_github.register(
            name='github',
            client_id=settings.github_client_id,
            client_secret=settings.github_client_secret,
            access_token_url='https://github.com/login/oauth/access_token',
            authorize_url='https://github.com/login/oauth/authorize',
            api_base_url='https://api.github.com/',
            client_kwargs={'scope': 'user:email'},
        )
    redirect_uri = request.url_for('github_callback')
    return await settings.oauth_github.github.authorize_redirect(request, redirect_uri)

@router.post("/register", response_model=UserRead, tags=["Authentication"])
async def create_user(user: UserCreate,  background_tasks: BackgroundTasks, code: Optional[str] = None, db: AsyncSession = Depends(get_db), redis_client: RedisClient = Depends(get_redis_client)):
    """Endpoint for registering new user

    Args:
        user (UserCreate): User details
        db (AsyncSession, optional)

    Raises:
        HTTPException: User already registered.
        HTTPException: Password and Email Validation Error.

    Returns:
        UserRead: User details except password
    """
    try:
        user_in_db = await db.execute(select(User).where(User.email == user.email))
        user_in_db = user_in_db.scalars().first()

        if user_in_db:
            logger.error("User already registered.")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already registered."
            )

        hashed_password = await get_password_hash(user.password)
        verification_required = True
        if code:
            verification_required = False

        db_user = User(
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            hashed_password=hashed_password,
            verified=not verification_required,
            phone_number=user.phone_number
        )

        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        
        if not code:
            background_tasks.add_task(
                send_email_verification,
                redis_client=redis_client,
                email=db_user.email,
                first_name=db_user.first_name,
                title="email_verification"
            )
            logger.info("User registered successfully. Verification email sent.")
            
        else:
            redis_code_value = await redis_client.get("invitation_email:" + code)
            json_object = json.loads(redis_code_value)
            return await add_user_to_organization(db_user.id, json_object.organization_id, json_object.role_id, db)
    except ValidationError as e:
        logger.error(f"Validation error: {e.errors()}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e.errors()
        )


@router.post("/login", response_model=Token, tags=["Authentication"])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    """Endpoint for login

    Args:
        form_data (OAuth2PasswordRequestForm, optional): User creds
        db (AsyncSession, optional)

    Raises:
        HTTPException: Authentication Error

    Returns:
        Token: Token details
    """

    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        logger.error("Incorrect email or password.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    
    access_token = await settings.auth_instance.create_access_token(
        data={"sub": form_data.username}, expires_delta=access_token_expires
    )
    refresh_token_expires = timedelta(days=settings.refresh_token_expire_days)
    refresh_token = await settings.auth_instance.create_refresh_token(
        data={"sub": form_data.username}, expires_delta=refresh_token_expires, db=db
    )
    
    logger.info(f"User {form_data.username} logged in successfully.")
    
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.post("/refresh-token", response_model=Token, tags=["Authentication"])
async def refresh_access_token(refresh_token: str, db: AsyncSession = Depends(get_db)):
    """Generate refresh token

    Args:
        refresh_token (str)
        db (AsyncSession, optional)

    Raises:
        credentials_exception: Unauthorized

    Returns:
        Token: Token Details
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(refresh_token, settings.secret_key, algorithms=[settings.algorithm])
        email: str = payload.get("sub")

        # Check token in database
        token_result = await db.execute(
            select(RefreshToken).where(RefreshToken.token == refresh_token, RefreshToken.revoked == False)
        )
        stored_token = token_result.scalars().first()
        if not stored_token or stored_token.expires_at < datetime.utcnow():
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        

    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = await settings.auth_instance.create_access_token(
        data={"sub": email}, expires_delta=access_token_expires
    )
    logger.info(f"Refreshed the token successfully for user {email}.")
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}



@router.get("/users/me", response_model=UserRead, tags=["Users"])
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/revoke-token", tags=["Authentication"])
async def revoke_refresh_token(refresh_token: str, db: AsyncSession = Depends(get_db)):
    update_statement = (
        update(RefreshToken)
        .where(RefreshToken.token == refresh_token)
        .values(revoked=True)
    )
    await db.execute(update_statement)
    await db.commit()
    logger.info(f"Token revoked successfully.")
    return {"message": "Token revoked successfully"}


@router.get('/google/callback')
async def google_auth_callback(request: Request, db: AsyncSession = Depends(get_db)):
    token = await settings.oauth_google.google.authorize_access_token(request)
    user_info = token.get('userinfo')
    if not user_info:
        raise HTTPException(status_code=400, detail="Failed to fetch user info")
    
    # Check if user exists, if not, create a new user
    user = await db.execute(select(User).where(User.email == user_info['email']))
    user = user.scalars().first()
    
    if not user:
        # Create a new user if not exists
        user = User(
            full_name=user_info['name'],
            email=user_info['email'],
            auth_type=AuthType.GOOGLE
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    # Generate tokens
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = await settings.auth_instance.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    refresh_token_expires = timedelta(days=settings.refresh_token_expire_days)
    refresh_token = await settings.auth_instance.create_refresh_token(
        data={"sub": user.email}, expires_delta=refresh_token_expires, db=db
    )

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get('/microsoft/callback')
async def microsoft_auth_callback(request: Request, db: AsyncSession = Depends(get_db)):
    token = await settings.oauth.microsoft.authorize_access_token(request)
    user_info = token.get('userinfo')
    if not user_info:
        raise HTTPException(status_code=400, detail="Failed to fetch user info")
    
    user = await db.execute(select(User).where(User.email == user_info['email']))
    user = user.scalars().first()
    
    if not user:
        # Create a new user if not exists
        user = User(
            full_name=user_info['name'],
            email=user_info['email'],
            auth_type=AuthType.GOOGLE
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    # Generate tokens
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = await settings.auth_instance.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    refresh_token_expires = timedelta(days=settings.refresh_token_expire_days)
    refresh_token = await settings.auth_instance.create_refresh_token(
        data={"sub": user.email}, expires_delta=refresh_token_expires, db=db
    )

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get('/github/callback')
async def github_callback(request: Request, db: AsyncSession = Depends(get_db)):
    """Handles the callback from GitHub after user authorization."""
    # Get access token from GitHub
    token = await settings.oauth_github.github.authorize_access_token(request)
    user_data = await settings.oauth_github.github.get('user', token=token)
    user_email = await settings.oauth_github.github.get('user/emails', token=token)
    user_info = user_data.json()
    user_email_info = user_email.json()

    email = None
    for email_info in user_email_info:
        if email_info.get('primary') and email_info.get('verified'):
            email = email_info.get('email')
            break

    if not email:
        raise HTTPException(status_code=400, detail="No verified email found.")

    user = await db.execute(select(User).where(User.email == email))
    user = user.scalars().first()

    if not user:
    # Create a new user if not exists
        user = User(
            full_name=user_info['name'],
            email=user_info['email'],
            auth_type=AuthType.GOOGLE
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    # Generate tokens
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = await settings.auth_instance.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    refresh_token_expires = timedelta(days=settings.refresh_token_expire_days)
    refresh_token = await settings.auth_instance.create_refresh_token(
        data={"sub": user.email}, expires_delta=refresh_token_expires, db=db
    )

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get("/verify-email", tags=["Authentication"])
async def verify_email(code: str, redis_client: RedisClient = Depends(get_redis_client), db: AsyncSession = Depends(get_db)):
    """
    Endpoint to verify email using the provided verification code.
    """
    response_data = ResponseData.model_construct(success=False, message="Email verification failed!")
    key = f"email_verification_code:{code}"
    value = await redis_client.get(key)

    if not value:
        logger.error(f"Verification code '{code}' not found or expired.")
        response_data.message = "Invalid or expired verification code."
        return response_data.dict()

    logger.info(f"Email successfully verified for code: {code}")
    stmt = update(User).where(User.email == value).values(verified=True)
    await db.execute(stmt)
    await db.commit()
    await redis_client.delete(key)
    response_data.success = True
    response_data.message = "Email verified successfully!"

    return response_data.dict()


@router.post("/forgot-password")
async def forgot_password(email: str, background_tasks: BackgroundTasks, redis_client=Depends(get_redis_client), db: AsyncSession = Depends(get_db)):
    """
    Initiates the process for a user to reset their password by sending a password reset email.

    Parameters:
    - email (str): The email address of the user who wants to reset their password.
    - background_tasks (BackgroundTasks): An instance to manage background tasks, used to send the email asynchronously.
    - redis_client: A dependency injection for the Redis client, used for caching or session management.
    - db (AsyncSession): A dependency injection for the database session, used to query the user information.

    Returns:
    - dict: A dictionary containing the success status and a message indicating the result of the operation.

    Raises:
    - No explicit exceptions are raised, but it assumes the presence of a user with the given email in the database.
    - If the user is not found, the function returns a message indicating "User not found".
    """
    response_data = ResponseData.model_construct(success=False, message="Failed to send password reset email")
    user = await db.execute(select(User).where(User.email == email))
    user = user.scalars().first()

    if not user:
        response_data.message("User not found")
        return response_data.dict()

    background_tasks.add_task(
        send_forgot_password_email,
        redis_client=redis_client,
        email=email,
        first_name=user.first_name,
        title="forgot_password"
    )
    logger.info("User registered successfully. Verification email sent.")
    response_data.success = True
    response_data.message = "Password reset email sent"
    return response_data.dict()


@router.post("/reset-password")
async def reset_password(code: str, new_password: str, redis_client=Depends(get_redis_client), db: AsyncSession = Depends(get_db)):
    """
    Resets the password for a user identified by a unique code.

    Parameters:
    - code (str): A unique string used to identify the password reset request.
    - new_password (str): The new password to be set for the user.
    - redis_client: A Redis client instance used to retrieve and delete the password reset code. 
      It is injected using dependency injection with `Depends(get_redis_client)`.
    - db (AsyncSession): An asynchronous database session used to execute the update query. 
      It is injected using dependency injection with `Depends(get_db)`.

    Returns:
    - dict: A dictionary containing the success status and a message indicating the result of the operation.

    Raises:
    - No explicit exceptions are raised, but it assumes that the Redis client and database operations 
      are successful. If the code is not found in Redis, it returns a failure message.
    """
    response_data = ResponseData.model_construct(success=False, message="Failed to reset password")
    
    email = await redis_client.get(f"forgot_password:{code}")

    if not email:
        response_data.message("User not found")
        return response_data.dict()

    hashed_password = await get_password_hash(new_password)
    stmt = update(User).where(User.email == email).values(hashed_password=hashed_password)
    await db.execute(stmt)
    await db.commit()

    await redis_client.delete(f"forgot_password:{code}")

    response_data.success = True
    response_data.message = "Password has been reset successfully"
    return response_data.dict()