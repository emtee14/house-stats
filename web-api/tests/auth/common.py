import pytest

from app.auth.native_auth_adapter import NativeAuthAdapter
from app.models.auth import User
from tests.common import db_session, engine, config


@pytest.fixture
def create_user(db_session, config):
    def _create(email: str, first_name: str, last_name: str, password: str):
        user = User(email=email, first_name=first_name, last_name=last_name)
        user.set_password(password)

        auth_adap = NativeAuthAdapter(db_session, config.SECRET_KEY, config.JWT_ALGORITHM)
        new_user = auth_adap.add_new_user(user)

        return new_user

    return _create