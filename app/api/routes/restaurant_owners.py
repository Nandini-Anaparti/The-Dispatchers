from fastapi import APIRouter, Depends, HTTPException
from app.api.routes.customers import get_user_service
from app.schemas.user import RestaurantOwnerRegister, User
from app.services.user_service import (
    UserService,
    EmailAlreadyRegisteredError
)

router = APIRouter(
    prefix="/restaurant-owners",
    tags=["restaurant-owners"]
)

@router.post(
    "",
    response_model=User,
    status_code=201,
    responses={409: {"description": "Email already registered"}}
)
def register_restaurant_owner(
    data: RestaurantOwnerRegister,
    service: UserService = Depends(get_user_service)
):
    """Register a restaurant owner account with an email and password."""
    try:
        return service.register_restaurant_owner(data)

    except EmailAlreadyRegisteredError:
        raise HTTPException(
            status_code=409,
            detail="Email already registered"
        )
