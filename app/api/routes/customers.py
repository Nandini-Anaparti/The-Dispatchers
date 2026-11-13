from fastapi import APIRouter, Depends, HTTPException

from app.core.config import get_users_data_path
from app.repositories.user_repository import UserRepository
from app.schemas.user import CustomerRegister, User
from app.services.user_service import (
    UserService,
    EmailAlreadyRegisteredError
)

router = APIRouter(
    prefix="/customers",
    tags=["customers"]
)

def get_user_service() -> UserService:
    repository = UserRepository(get_users_data_path())
    return UserService(repository)

@router.post(
    "",
    response_model=User,
    status_code=201,
    responses={409: {"description": "Email already registered"}}
)
def register_customer(
    data: CustomerRegister,
    service: UserService = Depends(get_user_service)
):
    try:
        return service.register_customer(data)
    except EmailAlreadyRegisteredError:
        raise HTTPException(
            status_code=409,
            detail="Email already registered"
        )
