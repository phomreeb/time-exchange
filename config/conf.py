from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    # Django Core
    SECRET_KEY: str = 'django-insecure-z1soqb6yc9=x6q9ohexx-jd#pa*wcz0_!83ut%zq8gu$16y6x='
    DEBUG: bool = True
    ALLOWED_HOSTS: list[str] = []

    # Database (Postgres)
    POSTGRES_DB: str = 'time_exchange'
    POSTGRES_USER: str = 'postgres'
    POSTGRES_PASSWORD: str = 'postgres'
    POSTGRES_HOST: str = 'localhost'
    POSTGRES_PORT: int = 5432

    # Redis
    REDIS_URL: str = 'redis://localhost:6379/0'

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / '.env',
        env_file_encoding='utf-8',
        extra='ignore'
    )

settings = Settings()