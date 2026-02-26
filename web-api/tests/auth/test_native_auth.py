import os
from typing import Any, Generator

import pytest
from sqlalchemy import text, Engine
from sqlmodel import Session, select, create_engine, SQLModel
from dotenv import load_dotenv

from app.auth.native_auth_adapter import NativeAuthAdapter
from app.config import Config
from app.models.auth import User
import jwt

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


def test_register_user(db_session, config):
    user = User(
        email="test-user@example.com",
        first_name="John",
        last_name="Doe",
    )
    user.set_password("MyVeryStrongPassword")

    auth_adap = NativeAuthAdapter(db_session, config.SECRET_KEY, config.JWT_ALGORITHM)
    new_user = auth_adap.add_new_user(user)

    assert new_user.id is not None
    assert new_user.email == user.email
    assert new_user.first_name == user.first_name
    assert new_user.last_name == user.last_name

def test_create_dupe_user(db_session, create_user, config):
    user = create_user(email="test@example.com", first_name="John", last_name="Doe", password="Password123")
    try:
        auth_adap = NativeAuthAdapter(db_session, config.SECRET_KEY, config.JWT_ALGORITHM)
        new_user = auth_adap.add_new_user(user)
    except ValueError as e:
        assert str(e) == "User with that email address already exists"

        res = db_session.exec(select(User).where(User.email == user.email).limit(2)).all()
        assert len(res) == 1

def test_fetch_by_email(db_session, create_user, config):
    email = "test@example.com"
    user = create_user(email=email, first_name="John", last_name="Doe", password="")

    auth_adap = NativeAuthAdapter(db_session, config.SECRET_KEY, config.JWT_ALGORITHM)

    fetched_user = auth_adap.get_user_by_email(email)
    assert fetched_user.email == email
    assert fetched_user.first_name == user.first_name
    assert fetched_user.last_name == user.last_name

def test_fetch_by_email_fail(db_session, create_user, config):
    email = "test@example.com"
    user = create_user(email=email, first_name="John", last_name="Doe", password="")

    auth_adap = NativeAuthAdapter(db_session, config.SECRET_KEY, config.JWT_ALGORITHM)

    fetched_user = auth_adap.get_user_by_email("incorrect-email@example.com")

    assert fetched_user is None

def test_login(db_session, create_user, config):
    email = "test@example.com"
    passwd = "Test-password-12328"

    auth_adap = NativeAuthAdapter(db_session, config.SECRET_KEY, config.JWT_ALGORITHM)

    user = create_user(email=email, first_name="John", last_name="Doe", password=passwd)
    token = auth_adap.login(email, passwd)


    decoded_data = jwt.decode(token, config.SECRET_KEY, algorithms=[config.JWT_ALGORITHM])
    assert decoded_data.get("user_id") == user.id.hex


def test_bad_email_login(db_session, create_user, config):
    email = "test@example.com"
    passwd = "Test-password-12328"
    auth_adap = NativeAuthAdapter(db_session, config.SECRET_KEY, config.JWT_ALGORITHM)

    user = create_user(email=email, first_name="John", last_name="Doe", password=passwd)

    with pytest.raises(ValueError, match="Incorrect email or password"):
        auth_adap.login("incorrect_email@example.com", passwd)

def test_bad_password_login(db_session, create_user, config):
    email = "test@example.com"
    passwd = "Test-password-12328"
    auth_adap = NativeAuthAdapter(db_session, config.SECRET_KEY, config.JWT_ALGORITHM)

    user = create_user(email=email, first_name="John", last_name="Doe", password=passwd)

    with pytest.raises(ValueError, match="Incorrect email or password"):
        auth_adap.login(email, "incorrect_password")

