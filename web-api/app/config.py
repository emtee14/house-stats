import os
from dotenv import load_dotenv

load_dotenv(".env.dev")


class Config:
    DATABASE_URL: str = os.environ.get("DATABASE_URL")
    SECRET_KEY: str = os.environ.get("SECRET_KEY")