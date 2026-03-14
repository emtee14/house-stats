import secrets
from datetime import timedelta
import time

import pytest

from app.auth.api_tokens import ApiTokenAuth
from tests.common import *
from tests.auth.common import create_user

def test_new_token(db_session, create_user):
    user = create_user("test@example.com", "test", "user", "test-password")

    token_adap = ApiTokenAuth(db_session)

    token_str, token_record = token_adap.create_token(user)

    assert token_str is not None
    assert token_record is not None

    assert token_record.user_id == user.id
    assert token_record.id == token_str.split(".")[0]

def test_revoke_token(db_session, create_user):
    user = create_user("test@example.com", "test", "user", "test-password")

    token_adap = ApiTokenAuth(db_session)

    token_str, token_record = token_adap.create_token(user)

    assert token_record.revoked is False

    token_adap.revoke_token(user, token_str)
    assert token_record.revoked is True

def test_revoke_revoked_token(db_session, create_user):
    user = create_user("test@example.com", "test", "user", "test-password")

    token_adap = ApiTokenAuth(db_session)

    token_str, token_record = token_adap.create_token(user)

    assert token_record.revoked is False
    token_adap.revoke_token(user, token_str)

    with pytest.raises(ValueError, match="Token is revoked"):
        token_adap.revoke_token(user, token_str)

def test_revoke_invalid_token(db_session, create_user):
    user = create_user("test@example.com", "test", "user", "test-password")

    token_adap = ApiTokenAuth(db_session)

    token_str, token_record = token_adap.create_token(user)

    assert token_record.revoked is False
    with pytest.raises(ValueError, match="Invalid token"):
        token_adap.revoke_token(user, "gobbledy-gook")

def test_verify_valid_token(db_session, create_user):
    user = create_user("test@example.com", "test", "user", "test-password")

    token_adap = ApiTokenAuth(db_session)

    token_str, token_record = token_adap.create_token(user)

    api_token = token_adap.verify_token(token_str)

    assert api_token is not None
    assert api_token.user_id == user.id

def test_verify_expired_token(db_session, create_user):
    user = create_user("test@example.com", "test", "user", "test-password")

    token_adap = ApiTokenAuth(db_session)

    token_str, token_record = token_adap.create_token(user, expiry=timedelta(milliseconds=1))
    time.sleep(0.1)

    with pytest.raises(ValueError, match="Token expired"):
        token_adap.verify_token(token_str)

def test_verify_invalid_token(db_session, create_user):
    create_user("test@example.com", "test", "user", "test-password")

    token_adap = ApiTokenAuth(db_session)

    with pytest.raises(ValueError, match="Invalid token"):
        token_adap.verify_token("not a valid token")

def test_verify_no_existing_token(db_session, create_user):
    user = create_user("test@example.com", "test", "user", "test-password")

    token_adap = ApiTokenAuth(db_session)
    token_str, token_record = token_adap.create_token(user)
    db_session.delete(token_record)

    with pytest.raises(ValueError, match="Unable to find token"):
        token_adap.verify_token(token_str)

def test_verify_invalid_hash(db_session, create_user):
    user = create_user("test@example.com", "test", "user", "test-password")

    token_adap = ApiTokenAuth(db_session)
    token_str, token_record = token_adap.create_token(user)

    token_str = secrets.token_urlsafe(32)

    invalid_token_str = f"{token_record.id}.{token_str}"

    with pytest.raises(ValueError, match="Invalid token"):
        token_adap.verify_token(invalid_token_str)

def test_verify_revoked_token(db_session, create_user):
    user = create_user("test@example.com", "test", "user", "test-password")

    token_adap = ApiTokenAuth(db_session)
    token_str, token_record = token_adap.create_token(user)
    token_record.revoked = True

    with pytest.raises(ValueError, match="Token is revoked"):
        token_adap.verify_token(token_str)