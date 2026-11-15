import os
from datetime import datetime, timedelta, timezone
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import get_users_data_path
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserInDB

bearer_scheme = HTTPBearer(auto_error=False)

def create_access_token(user_id: int) -> str:
    payload = {
        "sub": str(user_id),
        "exp": datetime.now(timezone.utc) + timedelta(hours=1)
    }

    return jwt.encode(
        payload,
        os.environ["AUTH_SECRET_KEY"],
        algorithm="HS256"
    )

def get_current_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme)) -> UserInDB:

    unauthorized = HTTPException(
        status_code=401,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"}
    )

    if credentials is None:
        raise unauthorized

    try:
        payload = jwt.decode(
            credentials.credentials,
            os.environ["AUTH_SECRET_KEY"],
            algorithms=["HS256"],
            options={"require": ["sub", "exp"]}
        )

        user_id = int(payload["sub"])

    except (jwt.InvalidTokenError, ValueError, TypeError):
        raise unauthorized

    repository = UserRepository(get_users_data_path())
    user = repository.get_by_id(user_id)

    if user is None or not user.is_active:
        raise unauthorized

    return user