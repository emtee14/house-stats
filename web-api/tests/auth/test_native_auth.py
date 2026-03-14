import pytest
from sqlmodel import select
import jwt

from app.auth.native_auth_adapter import NativeAuthAdapter
from app.models.auth import User
from tests.common import *
from tests.auth.common import create_user


def test_register_user(db_session, settings):
    user = User(
        email="test-user@example.com",
        first_name="John",
        last_name="Doe",
    )
    user.set_password("MyVeryStrongPassword")

    auth_adap = NativeAuthAdapter(db_session, settings.secret_key, settings.jwt_algorithm)
    new_user = auth_adap.add_new_user(user)

    assert new_user.id is not None
    assert new_user.email == user.email
    assert new_user.first_name == user.first_name
    assert new_user.last_name == user.last_name


def test_create_dupe_user(db_session, create_user, settings):
    user = create_user(
        email="test@example.com",
        first_name="John",
        last_name="Doe",
        password="Password123",
    )
    try:
        auth_adap = NativeAuthAdapter(
            db_session, settings.secret_key, settings.jwt_algorithm
        )
        auth_adap.add_new_user(user)
    except ValueError as e:
        assert str(e) == "User with that email address already exists."

        res = db_session.exec(
            select(User).where(User.email == user.email).limit(2)
        ).all()
        assert len(res) == 1


def test_fetch_by_email(db_session, create_user, settings):
    email = "test@example.com"
    user = create_user(email=email, first_name="John", last_name="Doe", password="")

    auth_adap = NativeAuthAdapter(db_session, settings.secret_key, settings.jwt_algorithm)

    fetched_user = auth_adap.get_user_by_email(email)
    assert fetched_user.email == email
    assert fetched_user.first_name == user.first_name
    assert fetched_user.last_name == user.last_name


def test_fetch_by_email_fail(db_session, create_user, settings):
    email = "test@example.com"
    create_user(email=email, first_name="John", last_name="Doe", password="")

    auth_adap = NativeAuthAdapter(db_session, settings.secret_key, settings.jwt_algorithm)

    fetched_user = auth_adap.get_user_by_email("incorrect-email@example.com")

    assert fetched_user is None


def test_login(db_session, create_user, settings):
    email = "test@example.com"
    passwd = "Test-password-12328"

    auth_adap = NativeAuthAdapter(db_session, settings.secret_key, settings.jwt_algorithm)

    user = create_user(email=email, first_name="John", last_name="Doe", password=passwd)
    jwt_token, refresh_token = auth_adap.login(email, passwd)

    decoded_data = jwt.decode(
        jwt_token, settings.secret_key, algorithms=[settings.jwt_algorithm]
    )
    assert decoded_data.get("user_id") == user.id.hex


def test_bad_email_login(db_session, create_user, settings):
    email = "test@example.com"
    passwd = "Test-password-12328"
    auth_adap = NativeAuthAdapter(db_session, settings.secret_key, settings.jwt_algorithm)

    create_user(email=email, first_name="John", last_name="Doe", password=passwd)

    with pytest.raises(ValueError, match="Incorrect email or password"):
        auth_adap.login("incorrect_email@example.com", passwd)


def test_bad_password_login(db_session, create_user, settings):
    email = "test@example.com"
    passwd = "Test-password-12328"
    auth_adap = NativeAuthAdapter(db_session, settings.secret_key, settings.jwt_algorithm)

    create_user(email=email, first_name="John", last_name="Doe", password=passwd)

    with pytest.raises(ValueError, match="Incorrect email or password"):
        auth_adap.login(email, "incorrect_password")
