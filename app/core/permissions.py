from typing import Annotated

from fastapi import Depends, HTTPException, Path
from app.core.auth import get_current_user
from app.schemas.user import UserInDB

RestaurantId = Annotated[int, Path(description="ID of the restaurant")]

def require_customer(current_user: UserInDB = Depends(get_current_user)) -> UserInDB:
    if current_user.role != "customer":
        raise HTTPException(status_code=403, detail="Customer access required")

    return current_user

def require_admin(current_user: UserInDB = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )

    return current_user

def require_restaurant_access(
    restaurant_id: RestaurantId,
    current_user: UserInDB = Depends(get_current_user)
):
    if current_user.role == "admin":
        return current_user

    if current_user.role == "restaurant owner":
        if restaurant_id in current_user.restaurant_ids:
            return current_user

    raise HTTPException(
        status_code=403,
        detail="You do not have permission to manage this restaurant"
    )

def require_restaurant_creator(
    current_user: UserInDB = Depends(get_current_user)
):
    if current_user.role not in ("restaurant owner", "admin"):
        raise HTTPException(
            status_code=403,
            detail="Only restaurant owners and admins can create restaurants"
        )

    return current_user
