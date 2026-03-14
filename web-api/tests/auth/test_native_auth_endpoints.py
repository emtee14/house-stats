from datetime import datetime, timedelta

from dateutil.tz import UTC
from fastapi.testclient import TestClient
from sqlmodel import select

from app.auth.native_auth_adapter import NativeAuth
from tests.common import *

from app.models.auth import User


def test_register_user_e2e(client: TestClient, db_session):
    email = "test-user@example.com"

    resp = client.post("/auth/register",
                json={
                    "email": email,
                    "password": "password",
                    "first_name": "Test",
                    "last_name": "User",
                }
            )


    assert resp.status_code == 200
    assert resp.json()["msg"] == "Successfully created user, please login to continue"

    stmt = select(User).where(User.email == email).limit(1)
    user = db_session.exec(stmt).one_or_none()

    assert user is not None
    assert user.first_name == "Test"
    assert user.last_name == "User"

def test_login_user_e2e(client: TestClient, db_session, settings):

    email = "test@example.com"
    password = "test-password"


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

    stmt = select(User).where(User.email == email).limit(1)
    user = db_session.exec(stmt).one_or_none()

    resp_login = client.post("/auth/login",
                       json={
                           "email": email,
                           "password": password
                       }
                       )

    assert resp_login.status_code == 200
    assert resp_login.json()["access_token"] is not None

    auth_adap = NativeAuth(db_session, settings.secret_key, settings.jwt_algorithm)

    resp = auth_adap.verify_jwt(resp_login.json()["access_token"])
    assert resp["user_id"] == user.id.hex


def test_login_invalid_user_e2e(client: TestClient):

    resp_login = client.post("/auth/login",
                             json={
                                 "email": "gobedly",
                                 "password": "gook"
                             }
                             )

    assert resp_login.status_code == 400
    assert resp_login.json()["detail"] == "Incorrect email or password."


def test_login_invalid_password_e2e(client: TestClient):

    email = "test@example.com"

    resp_register = client.post("/auth/register",
                                json={
                                    "email": email,
                                    "password": "password",
                                    "first_name": "Test",
                                    "last_name": "User",
                                }
                                )
    assert resp_register.status_code == 200
    assert resp_register.json()["msg"] == "Successfully created user, please login to continue"

    resp_login = client.post("/auth/login",
                             json={
                                 "email": email,
                                 "password": "gook"
                             }
                             )

    assert resp_login.status_code == 400
    assert resp_login.json()["detail"] == "Incorrect email or password."

def test_refresh_token_e2e(client: TestClient, db_session, settings):
    email = "test@example.com"
    password = "test-password"

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

    resp_login = client.post("/auth/login",
                             json={
                                 "email": email,
                                 "password": password
                             }
                             )

    assert resp_login.status_code == 200
    assert resp_login.json()["access_token"] is not None

    resp_refresh = client.post("/auth/refresh",
                               cookies=resp_login.cookies,)

    assert resp_refresh.status_code == 200
    assert resp_refresh.json()["access_token"] is not None

    auth_adap = NativeAuth(db_session, settings.secret_key, settings.jwt_algorithm)
    res = auth_adap.verify_jwt(resp_refresh.json()["access_token"])

    stmt = select(User).where(User.email == email).limit(1)
    user = db_session.exec(stmt).one_or_none()

    assert res["user_id"] == user.id.hex



