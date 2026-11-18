from fastapi import APIRouter, Depends, HTTPException, Response
from app.core.config import get_users_data_path
from app.core.permissions import require_customer
from app.repositories.user_repository import UserRepository
from app.schemas.user import CustomerProfile, CustomerProfileUpdate, CustomerRegister, User, UserInDB
from app.services.user_service import (
    UserService,
    CustomerProfileUnavailableError,
    EmailAlreadyRegisteredError
)

router = APIRouter(
    prefix="/customers",
    tags=["customers"]
)

PROFILE_ERRORS = {
    401: {"description": "Missing or invalid authentication, or account is inactive"},
    403: {"description": "Customer access required"},
}

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


@router.get("/me", response_model=CustomerProfile, responses=PROFILE_ERRORS)
def get_customer_profile(current_user: UserInDB = Depends(require_customer)) -> CustomerProfile:
    """Return the signed-in customer's account information."""
    return CustomerProfile.model_validate(current_user, from_attributes=True)


@router.put("/me", response_model=CustomerProfile, responses=PROFILE_ERRORS)
def update_customer_profile(
    data: CustomerProfileUpdate,
    current_user: UserInDB = Depends(require_customer),
    service: UserService = Depends(get_user_service),
) -> CustomerProfile:
    """Save the signed-in customer's name and optional delivery address."""
    try:
        return service.update_customer_profile(current_user.id, data)
    except CustomerProfileUnavailableError as exc:
        raise customer_profile_unavailable() from exc


@router.post("/me/deactivate", status_code=204, responses=PROFILE_ERRORS)
def deactivate_customer(
    current_user: UserInDB = Depends(require_customer),
    service: UserService = Depends(get_user_service),
) -> Response:
    """Deactivate the signed-in customer's account while retaining its record."""
    try:
        service.deactivate_customer(current_user.id)
    except CustomerProfileUnavailableError as exc:
        raise customer_profile_unavailable() from exc
    return Response(status_code=204)


def customer_profile_unavailable() -> HTTPException:
    return HTTPException(
        status_code=401,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )
