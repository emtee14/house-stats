import pytest

from app.auth.native_auth_adapter import NativeAuth
from app.models.auth import User
from tests.common import *


@pytest.fixture
def create_user(db_session, settings):
    def _create(email: str, first_name: str, last_name: str, password: str):
        user = User(email=email, first_name=first_name, last_name=last_name)
        user.set_password(password)

        auth_adap = NativeAuth(
            db_session, settings.secret_key, settings.jwt_algorithm
        )
        new_user = auth_adap.add_new_user(user)

        return new_user

    return _create


@pytest.fixture
def login_user(db_session, settings):
    def _login(email: str, password: str):
        auth_adap = NativeAuth(
            db_session, settings.secret_key, settings.jwt_algorithm
        )
        jwt, _ = auth_adap.login(email, password)

        return jwt

    return _login