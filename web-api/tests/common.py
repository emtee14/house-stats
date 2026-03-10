from typing import Generator

import pytest
from sqlalchemy import create_engine, Engine, text
from sqlmodel import SQLModel, Session

from app.config import Config


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
