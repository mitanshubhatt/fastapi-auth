from fastapi import Depends, BackgroundTasks, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from auth.models import User
from auth.services import AuthService
from auth.schemas import UserCreate, ForgotPasswordRequest, ResetPasswordRequest
from db.pg_connection import get_db
from auth.dependencies import get_current_user, get_redis_client
from db.redis_connection import RedisClient
from utils.serializers import ResponseData


def get_auth_service(
    redis_client: RedisClient = Depends(get_redis_client),
    db: AsyncSession = Depends(get_db)
) -> AuthService:
    return AuthService(db=db, redis_client=redis_client)


async def register_user(
    user: UserCreate,
    background_tasks: BackgroundTasks,
    code: Optional[str] = None,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Register new user"""
    result = await auth_service.register_user(user, background_tasks, code)
    return result


async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Authenticate user and return tokens"""
    result = await auth_service.authenticate_and_create_tokens(form_data)
    return result


async def refresh_token(
    refresh_token: str,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Refresh access token"""
    result = await auth_service.refresh_user_token(refresh_token)
    return result


async def revoke_token(
    refresh_token: str,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Revoke refresh token"""
    result = await auth_service.revoke_user_token(refresh_token)
    return result


async def verify_email(
    code: str,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Verify user email"""
    result = await auth_service.verify_user_email(code)
    return result


async def forgot_password(
    request: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Initiate password reset"""
    result = await auth_service.initiate_password_reset(request.email, background_tasks)
    return result


async def reset_password(
    request: ResetPasswordRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Reset user password"""
    result = await auth_service.reset_user_password(request.code, request.new_password)
    return result


# OAuth views
async def microsoft_login(
    request: Request,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Initiate Microsoft OAuth login"""
    return await auth_service.handle_microsoft_login(request)


async def microsoft_callback(
    request: Request,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Handle Microsoft OAuth callback"""
    result = await auth_service.handle_microsoft_callback(request)
    return result


async def google_login(
    request: Request,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Initiate Google OAuth login"""
    return await auth_service.handle_google_login(request)


async def google_callback(
    request: Request,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Handle Google OAuth callback"""
    result = await auth_service.handle_google_callback(request)
    return result


async def github_login(
    request: Request,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Initiate GitHub OAuth login"""
    return await auth_service.handle_github_login(request)


async def github_callback(
    request: Request,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Handle GitHub OAuth callback"""
    result = await auth_service.handle_github_callback(request)
    return result
