from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional
from utils.base_auth import BaseAuth

from authlib.integrations.starlette_client import OAuth


class Settings(BaseSettings):
    access_token_expire_minutes: int
    refresh_token_expire_days: int
    secret_key: str
    algorithm: str
    database_url: str
    auth_mode: str
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

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()
