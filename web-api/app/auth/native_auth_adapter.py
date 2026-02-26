from datetime import timedelta, datetime

from dateutil.tz import UTC
from sqlmodel import Session, select
import jwt

from app.auth.base import AuthBase
from app.models.auth import User


class NativeAuthAdapter(AuthBase):
    def __init__(self, session: Session, secret_key: str, algorithm: str = "HS256") -> None:
        self.session = session
        self._secret_key = secret_key
        self._algorithm = algorithm

    def get_user_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email).limit(1)
        user = self.session.exec(stmt).one_or_none()

        return user

    def add_new_user(self, user: User) -> User:
        dupe = self.get_user_by_email(user.email)
        if dupe is not None:
            raise ValueError("User with that email address already exists.")

        self.session.add(user)
        self.session.commit()

        return user

    def _create_jwt_token(self, payload: dict, expires_delta: timedelta = timedelta(minutes=5)):
        data_to_encode = payload.copy()
        data_to_encode.update({"exp": datetime.now(UTC) + expires_delta})

        encoded_jwt = jwt.encode(data_to_encode, self._secret_key, self._algorithm)

        return encoded_jwt

    def login(self, username: str, password: str) -> str:
        user = self.get_user_by_email(username)

        if user is None:
            raise ValueError("Incorrect email or password.")

        if not user.check_password(password):
            raise ValueError("Incorrect email or password.")

        token = self._create_jwt_token({"user_id": user.id.hex}, expires_delta=timedelta(minutes=5))

        return token

    def logout(self,) -> None:
        # TODO implement token binning
        pass

    def delete_user(self, user: User) -> None:
        # TODO add user deletion
        pass