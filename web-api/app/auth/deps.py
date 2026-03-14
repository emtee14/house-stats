
from fastapi import Depends, status, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.auth.api_tokens import ApiTokenAuth
from app.auth.native_auth_adapter import NativeAuth
from app.settings import get_settings, Settings
from app.db import get_session
from app.models.auth import User

security = HTTPBearer(auto_error=False)


def _get_current_user(
        allow_api_token: bool,
        credentials: HTTPAuthorizationCredentials | None,
        session: Session,
        settings: Settings,
) -> User:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication credentials",
        )

    if allow_api_token:
        try:
            token_adap = ApiTokenAuth(session)
            api_token = token_adap.verify_token(credentials.credentials)
            if api_token is not None:
                return api_token.user
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found for provided token",
                )
        except ValueError:
            pass

    # Normal JWT auth
    auth_adapter = NativeAuth(session, settings.secret_key, settings.jwt_algorithm)

    try:
        payload = auth_adapter.verify_jwt(credentials.credentials)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token",
        )

    user = auth_adapter.get_user(payload["user_id"])

    if user is not None:
        return user
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found for provided token",
        )


def get_current_user(
        credentials: HTTPAuthorizationCredentials | None = Depends(security),
        session: Session = Depends(get_session),
        settings: Settings = Depends(get_settings)
) -> User:
    return _get_current_user(
        allow_api_token=False,
        credentials=credentials,
        session=session,
        settings=settings,
    )


def get_current_user_with_api_token(
        credentials: HTTPAuthorizationCredentials | None = Depends(security),
        session: Session = Depends(get_session),
        settings: Settings = Depends(get_settings)
) -> User:
    return _get_current_user(
        allow_api_token=True,
        credentials=credentials,
        session=session,
        settings=settings,
    )
