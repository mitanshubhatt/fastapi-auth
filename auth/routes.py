from fastapi import APIRouter, Depends, Request, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from db.pg_connection import get_db
from auth.models import User
from auth.schemas import UserCreate, UserRead, Token
from auth.dependencies import get_current_user, get_redis_client
from auth.views import (
    register_user, login_user, refresh_token, revoke_token, verify_email,
    forgot_password, reset_password, microsoft_login, microsoft_callback,
    google_login, google_callback, github_login, github_callback
)
from db.redis_connection import RedisClient

router = APIRouter(prefix="/auth", tags=["Authentication"])

async def create_user(
    user: UserCreate, 
    background_tasks: BackgroundTasks, 
    code: Optional[str] = None, 
    db: AsyncSession = Depends(get_db), 
    redis_client: RedisClient = Depends(get_redis_client)
):
    return await auth_views.create_user(user, background_tasks, code, db, redis_client)

async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: AsyncSession = Depends(get_db)
):
    return await auth_views.login_for_access_token(form_data, db)

async def read_users_me(current_user: User = Depends(get_current_user)):
    return await auth_views.read_users_me(current_user)

# User authentication routes
router.add_api_route("/register", endpoint=register_user, methods=["POST"])
router.add_api_route("/login", endpoint=login_user, methods=["POST"])
router.add_api_route("/refresh", endpoint=refresh_token, methods=["POST"])
router.add_api_route("/revoke", endpoint=revoke_token, methods=["POST"])
router.add_api_route("/verify-email", endpoint=verify_email, methods=["POST"])
router.add_api_route("/forgot-password", endpoint=forgot_password, methods=["POST"])
router.add_api_route("/reset-password", endpoint=reset_password, methods=["POST"])

# OAuth routes
router.add_api_route("/microsoft", endpoint=microsoft_login, methods=["GET"])
router.add_api_route("/microsoft/callback", endpoint=microsoft_callback, methods=["GET"])
router.add_api_route("/google", endpoint=google_login, methods=["GET"])
router.add_api_route("/google/callback", endpoint=google_callback, methods=["GET"])
router.add_api_route("/github", endpoint=github_login, methods=["GET"])
router.add_api_route("/github/callback", endpoint=github_callback, methods=["GET"]) 