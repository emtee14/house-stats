from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.db import get_session
from app.models.auth import User
from app.routes.schemas.auth import LoginRequest, LoginResponse, RegisterUserRequest, RegisterUserResponse
from app.auth.native_auth_adapter import NativeAuthAdapter

from app.config import Config

@router.post("/register")
def register_user():
    pass


# ======== Native authentication routes ========
@router.post("/register",
             responses={
                 400: {
                     "description": "A user has already been created with that email",
                     "content": {
                         "application/json": {
                             "example": {"detail": "User with that email address already exists."}
                         }
                     },
                 }
             }
)
def register_user(request: RegisterUserRequest, session: Session = Depends(get_session)) -> RegisterUserResponse:
    auth_adapter = NativeAuthAdapter(session, Config.SECRET_KEY, Config.JWT_ALGORITHM)

    user = User(
        email=request.email,
        first_name=request.first_name,
        last_name=request.last_name,
    )
    user.set_password(request.password)

    try:
        auth_adapter.add_new_user(user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return RegisterUserResponse()


@router.post("/login",
             responses={
                 400: {
                     "description": "Incorrect email or password provided",
                     "content": {
                         "application/json": {
                             "example": {"detail": "Incorrect email or password."}
                         }
                     },
                 }
             }
             )
def login_user(request: LoginRequest, session: Session = Depends(get_session)):
    auth_adapter = NativeAuthAdapter(session, Config.SECRET_KEY, Config.JWT_ALGORITHM)

    try:
        token = auth_adapter.login(request.username, request.password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return LoginResponse(access_token=token)

@router.post("/refresh")
def refresh_token():
    pass

@router.post("/logout")
def logout_user():
    pass


@router.get("/oauth/{provider}/login")
def oauth_login(provider: str):
    pass

@router.get("/oauth/{provider}/callback")
def oauth_callback(provider: str):
    pass