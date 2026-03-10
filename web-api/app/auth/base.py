from abc import abstractmethod, ABC
from datetime import timedelta

from app.models.auth import User


class AuthBase(ABC):
    @abstractmethod
    def get_user_by_email(self, email) -> User | None:
        pass

    @abstractmethod
    def add_new_user(self, user: User) -> User:
        pass

    @abstractmethod
    def _create_jwt_token(
        self, payload: dict, expires_delta: timedelta = timedelta(minutes=5)
    ):
        pass

    @abstractmethod
    def login(self, username: str, password: str) -> str:
        pass

    @abstractmethod
    def logout(self, token: str) -> None:
        pass
