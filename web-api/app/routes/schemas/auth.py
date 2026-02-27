from pydantic import BaseModel

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str


class RegisterUserRequest(BaseModel):
    email: str
    password: str
    first_name: str
    last_name: str

class RegisterUserResponse(BaseModel):
    msg: str = "Successfully created user, please login to continue"