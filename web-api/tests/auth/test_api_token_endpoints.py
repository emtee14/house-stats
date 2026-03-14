from datetime import datetime, timedelta

from dateutil.tz import UTC
from fastapi.testclient import TestClient
from sqlmodel import select

from app.auth.native_auth_adapter import NativeAuth
from tests.common import *

from app.models.auth import User, ApiToken


def test_create_api_token_e2e(client: TestClient, db_session, settings):
    email = "test@example.com"
    password = "test-password"

    # Register user
    resp_register = client.post("/auth/register",
                                json={
                                    "email": email,
                                    "password": password,
                                    "first_name": "Test",
                                    "last_name": "User",
                                }
                                )
    assert resp_register.status_code == 200
    assert resp_register.json()["msg"] == "Successfully created user, please login to continue"

    # Login user
    resp_login = client.post("/auth/login",
                             json={
                                 "email": email,
                                 "password": password
                             }
                             )
    assert resp_login.status_code == 200
    assert resp_login.json()["access_token"] is not None

    # Create API token
    resp_create = client.post("/auth/token/create",
                              json={"name": "test-token", "expiry": 30},
                              headers={"Authorization": f"Bearer {resp_login.json()['access_token']}"}
                              )

    assert resp_create.status_code == 200
    response_data = resp_create.json()
    assert "token" in response_data
    assert "expiry" in response_data

    token_str = response_data["token"]
    assert token_str is not None

    # Verify token was created in DB
    stmt = select(User).where(User.email == email).limit(1)
    user = db_session.exec(stmt).one_or_none()
    assert user is not None

    stmt = select(ApiToken).where(ApiToken.user_id == user.id)
    tokens = db_session.exec(stmt).all()
    assert len(tokens) == 1

    token_record = tokens[0]
    assert token_record.id == token_str.split(".")[0]
    assert token_record.revoked is False
    assert token_record.expires_at > datetime.now(UTC)


def test_revoke_api_token_e2e(client: TestClient, db_session, settings):
    email = "test@example.com"
    password = "test-password"

    # Register user
    resp_register = client.post("/auth/register",
                                json={
                                    "email": email,
                                    "password": password,
                                    "first_name": "Test",
                                    "last_name": "User",
                                }
                                )
    assert resp_register.status_code == 200
    assert resp_register.json()["msg"] == "Successfully created user, please login to continue"

    # Login user
    resp_login = client.post("/auth/login",
                             json={
                                 "email": email,
                                 "password": password
                             }
                             )
    assert resp_login.status_code == 200
    assert resp_login.json()["access_token"] is not None

    # Create API token
    resp_create = client.post("/auth/token/create",
                              json={"name": "test-token", "expiry": 30},
                              headers={"Authorization": f"Bearer {resp_login.json()['access_token']}"}
                              )
    assert resp_create.status_code == 200
    token_str = resp_create.json()["token"]

    # Revoke API token
    resp_revoke = client.post("/auth/token/delete",
                              json={"token_id": token_str.split(".")[0]},
                              headers={"Authorization": f"Bearer {resp_login.json()['access_token']}"}
                              )

    assert resp_revoke.status_code == 200
    assert resp_revoke.json()["msg"] == "Successfully revoked token"

    # Verify token was revoked in DB
    stmt = select(User).where(User.email == email).limit(1)
    user = db_session.exec(stmt).one_or_none()
    assert user is not None

    stmt = select(ApiToken).where(ApiToken.user_id == user.id)
    tokens = db_session.exec(stmt).all()
    assert len(tokens) == 1

    token_record = tokens[0]
    assert token_record.revoked is True


def test_revoke_invalid_api_token_e2e(client: TestClient, db_session, settings):
    email = "test@example.com"
    password = "test-password"

    # Register user
    resp_register = client.post("/auth/register",
                                json={
                                    "email": email,
                                    "password": password,
                                    "first_name": "Test",
                                    "last_name": "User",
                                }
                                )
    assert resp_register.status_code == 200
    assert resp_register.json()["msg"] == "Successfully created user, please login to continue"

    # Login user
    resp_login = client.post("/auth/login",
                             json={
                                 "email": email,
                                 "password": password
                             }
                             )
    assert resp_login.status_code == 200
    assert resp_login.json()["access_token"] is not None

    # Try to revoke invalid token
    resp_revoke = client.post("/auth/token/delete",
                              json={"token_id": "invalid-token-id"},
                              headers={"Authorization": f"Bearer {resp_login.json()['access_token']}"}
                              )

    assert resp_revoke.status_code == 400
