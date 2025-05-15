from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional, Dict
from auth.strategies.base_auth import BaseAuth

from authlib.integrations.starlette_client import OAuth
from db.redis_connection import RedisClient


class Settings(BaseSettings):
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 1
    secret_key: str = "oGZGMadkunyMgtSxgV8dFg2UWkaqxYUvopvsvK7axrm61UekefE7mQrhQLJTt37E"
    algorithm: str = "HS256"
    database_url: str = "postgresql+asyncpg://postgres:postgres@127.0.0.1:5432/fast_auth"
    auth_mode: str = "jwt"
    encryption_key: str = "lOWuM2K1nGFOzzL+33Nm67Aa55ZaTB37glUeZIbVCmY="
    paseto_private_key: Optional[str] = None
    paseto_public_key: Optional[str] = None
    auth_instance: Optional[BaseAuth] = None
    google_client_id: Optional[str] = None
    google_client_secret: Optional[str] = None
    microsoft_client_id: Optional[str] = None
    microsoft_client_secret: Optional[str] = None
    github_client_id: Optional[str] = None
    github_client_secret: Optional[str] = None
    
    oauth_google: Optional[OAuth] = None
    oauth_microsoft: Optional[OAuth] = None
    oauth_github: Optional[OAuth] = None
    redis_database_url: Optional[str] = None
    hinata_host: Optional[str] = None
    email_provider: str = "netcore"
    smtp_from_email: str = "no-reply@gofynd.com"
    smtp_netcore: Optional[str] = None
    
    roles: Optional[Dict] = None
    
    redis_client: Optional[RedisClient] = None
    
    permissions: Optional[Dict] = None

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()
