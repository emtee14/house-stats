import os
from dotenv import load_dotenv


if os.environ.get("ENV") == "dev":
    load_dotenv(".env.dev")
elif os.environ.get("ENV") == "test":
    load_dotenv(".env.test")


class Config:
    DATABASE_URL: str = os.environ.get("DATABASE_URL")
    SECRET_KEY: str = os.environ.get("SECRET_KEY")
    JWT_ALGORITHM: str = os.environ.get("JWT_ALGORITHM")

    CELERY_RESULT_BACKEND: str = os.environ.get("CELERY_RESULT_BACKEND")
    CELERY_BROKER_URL: str = os.environ.get("CELERY_BROKER_URL")

    STRIPE_API_TOKEN: str = os.environ.get("STRIPE_API_TOKEN")
