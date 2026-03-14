from functools import lru_cache

from fastapi import Depends
from sqlmodel import create_engine, Session
from app.settings import Settings, get_settings



@lru_cache
def create_engine_from_url(database_url: str):
    return create_engine(database_url)


def create_engine_from_settings(settings: Settings):
    return create_engine_from_url(settings.database_url)


def get_engine(settings: Settings = Depends(get_settings)):
    return create_engine(settings.database_url)


def get_session(engine = Depends(get_engine)):
    with Session(engine) as session:
        yield session
