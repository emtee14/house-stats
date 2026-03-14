
from fastapi import Depends
from sqlmodel import create_engine, Session
from app.config import Settings, get_settings

def create_engine_from_settings(settings: Settings):
    return create_engine(settings.database_url)



def get_engine(settings: Settings = Depends(get_settings)):
    return create_engine(settings.database_url)


def get_session(engine = Depends(get_engine)):
    with Session(engine) as session:
        yield session
