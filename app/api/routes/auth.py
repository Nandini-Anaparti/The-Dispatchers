from fastapi import APIRouter, Depends, HTTPException
from app.api.routes.customers import get_user_service
from app.core.auth import create_access_token, get_current_user
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.user import User, UserInDB
from app.services.user_service import UserService

router = APIRouter(
    prefix="/auth",
    tags=["authentication"]
)

@router.post(
    "/login", response_model=TokenResponse,
    responses={401: {"description": "Invalid credentials or inactive account"}},
)
def login(
    data: LoginRequest,
    service: UserService = Depends(get_user_service)
):
    """Sign in with an email and password to obtain a bearer token."""
    user = service.authenticate_user(
        str(data.email),
        data.password
    )

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    token = create_access_token(user.id)

    return TokenResponse(access_token=token)

@router.get(
    "/me", response_model=User,
    responses={401: {"description": "Missing, invalid, or expired token, or inactive account"}},
)
def get_me(
    current_user: UserInDB = Depends(get_current_user)
):
    """Return the public account fields for the user identified by the bearer token."""
    return current_user
