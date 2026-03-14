from email_validator import validate_email, EmailNotValidError
from fastapi import APIRouter, Depends, HTTPException, Response, Cookie, status
from sqlmodel import Session

from app.auth.api_tokens import ApiTokenAuth
from app.auth.deps import get_current_user
from app.db import get_session
from app.models.auth import User
from app.routes.schemas.auth import (
    LoginRequest,
    LoginResponse,
    RegisterUserRequest,
    RegisterUserResponse,
    CreateApiTokenResponse,
    RevokeApiTokenRequest,
    RevokeApiTokenResponse,
)
from app.auth.native_auth_adapter import NativeAuth
from app.billing.stripe_adapter import StripePaymentAdapter
from app.settings import Settings, get_settings

router = APIRouter(tags=["Authentication"])


# ======== Native authentication routes ========
@router.post(
    "/register",
    response_model=RegisterUserResponse,
    summary="Register a new user",
    description="Creates a new user account with email and password authentication and initialises billing.",
    responses={
        400: {
            "description": "A user has already been created with that email",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "User with that email address already exists."
                    }
                }
            },
        }
    },
)
def register_user(
        request: RegisterUserRequest,
        session: Session = Depends(get_session),
        settings: Settings = Depends(get_settings)
) -> RegisterUserResponse:
    auth_adapter = NativeAuth(session, settings.secret_key, settings.jwt_algorithm)

    try:
        validate_email(request.email, check_deliverability=False)
    except EmailNotValidError as e:
        raise HTTPException(status_code=400, detail=str(e))

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

    payment_adap = StripePaymentAdapter(settings.stripe_api_token)
    payment_adap.setup_user(user, session)

    return RegisterUserResponse()


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="User login",
    description="Authenticates a user using email and password and returns a JWT access token while setting a refresh token cookie.",
    responses={
        400: {
            "description": "Incorrect email or password provided",
            "content": {
                "application/json": {
                    "example": {"detail": "Incorrect email or password."}
                }
            },
        }
    },
)
def login_user(
        request: LoginRequest, response: Response,
        session: Session = Depends(get_session),
        settings: Settings = Depends(get_settings)
):
    auth_adapter = NativeAuth(session, settings.secret_key, settings.jwt_algorithm)

    try:
        access_token, refresh_token = auth_adapter.login(
            request.email, request.password
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
    )

    return LoginResponse(access_token=access_token)


@router.post(
    "/refresh",
    response_model=LoginResponse,
    summary="Refresh access token",
    description="Uses the refresh token cookie to generate a new JWT access token."
)
def refresh_jwt(
        refresh_token: str = Cookie(None),
        session: Session = Depends(get_session),
        settings: Settings = Depends(get_settings)
):
    if refresh_token is None:
        raise HTTPException(status_code=400, detail="No refresh token present")

    auth_adapter = NativeAuth(session, settings.secret_key, settings.jwt_algorithm)

    try:
        access_token = auth_adapter.refresh_token(refresh_token)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

    return LoginResponse(access_token=access_token)


@router.post(
    "/logout",
    summary="Logout user",
    description="Revokes the refresh token associated with the current session and logs the user out."
)
def logout_user(
        refresh_token: str = Cookie(None),
        session: Session = Depends(get_session),
        settings: Settings = Depends(get_settings)
):
    if refresh_token is None:
        raise HTTPException(status_code=400, detail="No refresh token present")

    auth_adapter = NativeAuth(session, settings.secret_key, settings.jwt_algorithm)

    try:
        auth_adapter.revoke_refresh_token(refresh_token)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return Response(status_code=status.HTTP_200_OK)


# ======== Token for MCP and interaction from a system ========
@router.post(
    "/token/create",
    response_model=CreateApiTokenResponse,
    summary="Create API token",
    description="Generates a new API token for the authenticated user for programmatic access (e.g., MCP integrations)."
)
def create_api_token(user: User = Depends(get_current_user),
                     session : Session = Depends(get_session)) -> CreateApiTokenResponse:
    api_token_adap = ApiTokenAuth(session)


    token_str, token_record = api_token_adap.create_token(user)

    return CreateApiTokenResponse(token=token_str, expiry=token_record.expires_at.strftime("%Y-%m-%d %H:%M:%S"))


@router.post(
    "/token/delete",
    response_model=RevokeApiTokenResponse,
    summary="Revoke API token",
    description="Revokes an API token belonging to the authenticated user so it can no longer be used for authentication."
)
def delete_api_token(request: RevokeApiTokenRequest, user: User = Depends(get_current_user),
                     session : Session = Depends(get_session)) -> RevokeApiTokenResponse:
    api_token_adap = ApiTokenAuth(session)

    try:
        api_token_adap.revoke_token(user, request.token)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return RevokeApiTokenResponse()
