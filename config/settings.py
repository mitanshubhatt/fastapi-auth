from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7
    secret_key: str = "oGZGMadkunyMgtSxgV8dFg2UWkaqxYUvopvsvK7axrm61UekefE7mQrhQLJTt37E"
    algorithm: str = "HS256"
    database_url: str = "postgresql+asyncpg://authdb_owner:0MFqZ9rjyEUX@ep-falling-dust-a1nu2soz.ap-southeast-1.aws.neon.tech/authdb"

    class Config:
        env_file = ".env"

settings = Settings()