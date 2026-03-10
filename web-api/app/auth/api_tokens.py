import hashlib
from datetime import datetime, UTC, timedelta
from typing import Tuple

from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.models.auth import User, ApiToken
import secrets
import re


class ApiTokenAuth():
    def __init__(self, session: Session) -> None:
        self._session = session
        self._re_pattern = re.compile(r'^[A-Za-z0-9_-]{11}\.[A-Za-z0-9_-]{43}$')

    def create_token(self, user: User, expiry: timedelta = timedelta(weeks=12)) -> Tuple[str, ApiToken]:
        issued_at = datetime.now(UTC)

        for _ in range(5):
            key_id = secrets.token_urlsafe(8)
            api_token = secrets.token_urlsafe(32)
            hashed_token = hashlib.sha256(api_token.encode()).digest()

            token_record = ApiToken(
                id = key_id,
                user_id = user.id,
                token_hash = hashed_token,
                issued_at = issued_at,
                expires_at = issued_at + expiry,
            )
            try:
                self._session.add(token_record)
                break
            except IntegrityError:
                self._session.rollback()
        else:
            raise ValueError("Unable to create unique token")

        user_token = f"{key_id}.{api_token}"

        self._session.commit()
        return user_token, token_record


    def verify_token(self, token_str: str) -> ApiToken:
        token_match = self._re_pattern.match(token_str)
        if token_match is None:
            raise ValueError("Invalid token")

        token_id, token_val = token_str.split(".")

        stmt = select(ApiToken).where(ApiToken.id == token_id).limit(1)
        token_record = self._session.exec(stmt).one_or_none()

        if token_record is None:
            raise ValueError("Unable to find token")

        if token_record.expires_at < datetime.now(UTC):
            raise ValueError("Token expired")

        if token_record.revoked is True:
            raise ValueError("Token is revoked")

        token_hash = hashlib.sha256(token_val.encode()).digest()
        if token_record.token_hash != token_hash:
            raise ValueError("Invalid token")

        return token_record

    def revoke_token(self, user: User, token_str: str) -> None:
        token_record = self.verify_token(token_str)

        if token_record.user_id != user.id:
            raise ValueError("Token does not belong to user")

        if token_record.revoked is True:
            raise ValueError("Token already revoked")

        token_record.revoked = True
        self._session.commit()
