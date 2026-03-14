import os
from typing import Generator

import pytest
from dotenv import load_dotenv
from sqlalchemy import create_engine, Engine, text
from sqlmodel import SQLModel, Session
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import RedisContainer
from fastapi.testclient import TestClient
from app.main import create_app
from app.settings import Settings, get_settings
from app.db import get_session


class FakeData:
    def __init__(self, sales):
        self.sales = sales



@pytest.fixture(scope="session")
def postgres_container():
    container = PostgresContainer("postgres:16")
    container.start()
    db_url = container.get_connection_url()

    # Export so Config picks it up
    os.environ["DATABASE_URL"] = db_url

    yield container
    container.stop()

# Redis testcontainer for Celery and Redis-based cache
@pytest.fixture(scope="session")
def redis_container():
    """
    Starts a temporary Redis container for tests.
    Used by Celery and Redis-based aggregation cache.
    """
    container = RedisContainer("redis:7")
    container.start()

    yield container

    container.stop()

@pytest.fixture
def redis_url(redis_container) -> str:
    host = redis_container.get_container_host_ip()
    port = redis_container.get_exposed_port(6379)
    return f"redis://{host}:{port}/0"

@pytest.fixture
def settings(postgres_container, redis_url) -> Settings:

    load_dotenv("./.env.test")

    return Settings(
        database_url=postgres_container.get_connection_url(),
        celery_backend_results=redis_url,
        celery_broker_url=redis_url,
        secret_key=os.environ.get("SECRET_KEY"),
        jwt_algorithm=os.environ.get("JWT_ALGORITHM"),
        stripe_api_token=os.environ.get("STRIPE_API_TOKEN"),
    )


@pytest.fixture
def engine(postgres_container) -> Engine:
    db_url = postgres_container.get_connection_url()
    engine = create_engine(db_url)

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
def client(settings, db_session):
    def override_settings():
        return settings

    def override_get_session():
        yield db_session

    app = create_app()

    app.dependency_overrides[get_settings] = override_settings
    app.dependency_overrides[get_session] = override_get_session

    with TestClient(app, base_url="https://testserver") as client:
        yield client

    app.dependency_overrides.clear()
