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

class CreateApiTokenRequest(BaseModel):
    expiry: str

class CreateApiTokenResponse(BaseModel):
    expiry: str
    token: str

class RevokeApiTokenRequest(BaseModel):
    token: str

class RevokeApiTokenResponse(BaseModel):
    msg: str = "Successfully revoked token"