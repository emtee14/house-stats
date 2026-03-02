from typing import Generator

import pytest
from sqlalchemy import create_engine, Engine, text
from sqlmodel import SQLModel, Session

from app.auth.native_auth_adapter import NativeAuthAdapter
from app.config import Config
from app.models.auth import User


class FakeData:
    def __init__(self, sales):
        self.sales = sales


@pytest.fixture
def config() -> Config:
    return Config()


@pytest.fixture
def engine(config) -> Engine:
    engine = create_engine(config.DATABASE_URL)

    with engine.connect() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS auth"))
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS billing"))
        conn.commit()
    SQLModel.metadata.create_all(engine)

    return engine

@pytest.fixture
def db_session(engine) -> Generator[Session]:
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def create_user(db_session, config):
    def _create(email: str, first_name: str, last_name: str, password: str):
        user = User(email=email, first_name=first_name, last_name=last_name)
        user.set_password(password)

        auth_adap = NativeAuthAdapter(db_session, config.SECRET_KEY, config.JWT_ALGORITHM)
        new_user = auth_adap.add_new_user(user)

        return new_user

    return _create