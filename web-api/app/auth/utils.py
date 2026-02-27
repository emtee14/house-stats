
from fastapi import Depends, Request, status, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.auth.native_auth_adapter import NativeAuthAdapter
from app.config import Config
from app.db import get_session
from app.models.auth import User

security = HTTPBearer()

def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
    session: Session = Depends(get_session)) -> User:

    auth_adapter = NativeAuthAdapter(session, Config.SECRET_KEY, Config.JWT_ALGORITHM)

    try:
        payload = auth_adapter.verify_jwt(credentials.credentials)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    user = auth_adapter.get_user(payload["user_id"])

    if user is not None:
        return user
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

