import bcrypt
from sqlmodel import Field, SQLModel
import uuid

class User(SQLModel, table=True):
    __tablename__ = "users"
    __table_args__ = {"schema": "auth"}

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(index=True)
    first_name: str = Field()
    last_name: str = Field()
    password: bytes = Field()

    def set_password(self, password: str):
        password_bytes = password.encode()
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password_bytes, salt)
        self.password = hashed_password

    def check_password(self, password: str) -> bool:
        return bcrypt.checkpw(password.encode(), self.password)
