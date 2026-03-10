from datetime import timedelta, datetime
from hashlib import sha256
from secrets import token_urlsafe
from typing import Tuple

import jwt
from dateutil.tz import UTC
from sqlmodel import Session, select

from app.auth.base import AuthBase
from app.models.auth import User, RefreshToken


class NativeAuthAdapter(AuthBase):
    def __init__(
        self, session: Session, secret_key: str, algorithm: str = "HS256"
    ) -> None:
        self._session = session
        self._secret_key = secret_key
        self._algorithm = algorithm

    def get_user_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email).limit(1)
        user = self._session.exec(stmt).one_or_none()

        return user

    def get_user(self, user_id: str) -> User | None:
        stmt = select(User).where(User.id == user_id).limit(1)
        user = self._session.exec(stmt).one_or_none()
        return user

    def add_new_user(self, user: User) -> User:
        dupe = self.get_user_by_email(user.email)
        if dupe is not None:
            raise ValueError("User with that email address already exists.")

        self._session.add(user)
        self._session.commit()

        return user

    def _create_jwt_token(
        self, user: User, expires_delta: timedelta = timedelta(minutes=5)
    ):
        data_to_encode = {
            "user_id": user.id.hex,
            "exp": datetime.now(UTC) + expires_delta,
        }

        encoded_jwt = jwt.encode(data_to_encode, self._secret_key, self._algorithm)

        return encoded_jwt

    def _create_refresh_token(self, user, expires_delta: timedelta = timedelta(days=7)):
        expires_at = datetime.now(UTC) + expires_delta
        token = token_urlsafe(32)
        token_record = RefreshToken(
            user_id=user.id,
            expires_at=expires_at,
        )
        token_record.set_token_hash(token)
        self._session.add(token_record)
        self._session.commit()

        return token

    def verify_jwt(self, token: str) -> dict:
        try:
            payload = jwt.decode(token, self._secret_key, algorithms=[self._algorithm])
            return payload
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError) as e:
            raise e  # ValueError("Signature invalid or expired")

    def _verify_refresh_token(self, token: str) -> RefreshToken | None:
        token_hash = sha256(token.encode()).digest()
        stmt = (
            select(RefreshToken).where(RefreshToken.token_hash == token_hash).limit(1)
        )

        refresh_token = self._session.exec(stmt).one_or_none()
        return refresh_token

    def refresh_token(self, token: str) -> str:
        refr_token = self._verify_refresh_token(token)
        if (
            refr_token is not None
            and refr_token.expires_at < datetime.now(UTC).now()
            and refr_token.revoked is False
        ):
            new_jwt = self._create_jwt_token(refr_token.user)
            return new_jwt
        else:
            raise ValueError("Incorrect refresh token.")

    def revoke_refresh_token(self, token: str) -> str:
        refr_token = self._verify_refresh_token(token)
        if refr_token is not None:
            refr_token.revoke_token()
            self._session.commit()
            return token
        else:
            raise ValueError("Incorrect refresh token.")

    def login(self, username: str, password: str) -> Tuple[str, str]:
        user = self.get_user_by_email(username)

        if user is None:
            raise ValueError("Incorrect email or password.")

        if not user.check_password(password):
            raise ValueError("Incorrect email or password.")

        token = self._create_jwt_token(user)
        refresh_token = self._create_refresh_token(user)

        return token, refresh_token

    def logout(self, refresh_token: str) -> None:
        # TODO implement token binning
        pass

    def delete_user(self, user: User) -> None:
        # TODO add user deletion
        pass
