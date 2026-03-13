from typing import List

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
    name: str
    expiry: int # Days

class CreateApiTokenResponse(BaseModel):
    token: str
    expiry: str


class RevokeApiTokenRequest(BaseModel):
    token_id: str

class RevokeApiTokenResponse(BaseModel):
    msg: str = "Successfully revoked token"


class Token(BaseModel):
    id: str
    name: str
    expiry: str
    revoked: bool

class ListApiTokenResponse(BaseModel):
    tokens: List[Token]