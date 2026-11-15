from fastapi import Depends, HTTPException
from app.core.auth import get_current_user
from app.schemas.user import UserInDB

def require_admin(current_user: UserInDB = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )

    return current_user

def require_restaurant_access(
    restaurant_id: int,
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