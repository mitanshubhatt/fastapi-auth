from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    access_token_expire_minutes: int
    refresh_token_expire_days: int
    secret_key: str
    algorithm: str
    database_url: str

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()
