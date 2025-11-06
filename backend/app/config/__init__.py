from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    database_url: Optional[str] = None
    postgres_user: Optional[str] = "library"
    postgres_password: Optional[str] = "library"
    postgres_db: Optional[str] = "library"
    postgres_host: Optional[str] = "db"
    postgres_port: Optional[int] = 5432

    class Config:
        env_file = ".env"
        case_sensitive = False


def get_database_url() -> str:
    settings = Settings()
    if settings.database_url:
        return settings.database_url
    return (
        f"postgresql+asyncpg://{settings.postgres_user}:{settings.postgres_password}"
        f"@{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}"
    )


settings = Settings()
