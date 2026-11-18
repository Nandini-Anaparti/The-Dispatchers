class CustomerNotFoundError(Exception):
    pass


class CustomerInactiveError(Exception):
    pass


def require_active_customer(user_repo, customer_id: int):
    """Shared rule used by cart and checkout: the customer must exist,
    be a customer, and be active. Returns the user."""
    user = next((u for u in user_repo.get_all() if u.id == customer_id), None)
    if user is None or user.role != "customer":
        raise CustomerNotFoundError()
    if not user.is_active:
        raise CustomerInactiveError()
    return user