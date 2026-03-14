from functools import lru_cache

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = ""
    secret_key: str = "dev-secret"
    jwt_algorithm: str = "HS256"

    celery_backend_results: str = ""
    celery_broker_url: str = ""

    stripe_api_token: str = ""

    model_config = SettingsConfigDict(env_file=".env")

load_dotenv()

@lru_cache
def get_settings():
    return Settings()