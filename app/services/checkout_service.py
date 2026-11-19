from dataclasses import dataclass

from pydantic import ValidationError

from app.repositories.cart_repository import CartRepository
from app.repositories.menu_item_repository import MenuItemRepository
from app.repositories.restaurant_repository import RestaurantRepository
from app.repositories.user_repository import UserRepository
from app.schemas.cart import Cart, CartView
from app.schemas.menu_item import MenuItem
from app.schemas.restaurant import Restaurant
from app.services.customer_rules import require_active_customer
from app.services.pricing import price_cart


class ActiveCartNotFoundError(Exception):
    pass


class CheckoutValidationError(Exception):
    pass


@dataclass(frozen=True)
class ValidatedCheckout:
    cart: Cart
    restaurant: Restaurant
    menu_items: dict[int, MenuItem]


class CheckoutService:
    def __init__(
        self,
        cart_repo: CartRepository,
        menu_repo: MenuItemRepository,
        restaurant_repo: RestaurantRepository,
        user_repo: UserRepository,
    ):
        self.cart_repo = cart_repo
        self.menu_repo = menu_repo
        self.restaurant_repo = restaurant_repo
        self.user_repo = user_repo

    def validate(self, customer_id: int) -> ValidatedCheckout:
        """Read and validate the current checkout inputs without writing any records."""
        require_active_customer(self.user_repo, customer_id)
        try:
            cart = self.cart_repo.get_active_by_customer(customer_id)
        except ValidationError as exc:
            raise CheckoutValidationError("Stored cart data is invalid") from exc
        if cart is None:
            raise ActiveCartNotFoundError()
        if not cart.items:
            raise CheckoutValidationError("The active cart is empty")

        restaurant = self.restaurant_repo.get_by_id(cart.restaurant_id) if cart.restaurant_id is not None else None
        if restaurant is None:
            raise CheckoutValidationError("The cart's restaurant does not exist")
        if not restaurant.is_open:
            raise CheckoutValidationError("The cart's restaurant is closed")

        menu = {item.id: item for item in self.menu_repo.get_by_restaurant(restaurant.id)}
        validated_items = {}
        for line in cart.items:
            item = menu.get(line.menu_item_id)
            if item is None or not item.is_active or not item.is_available:
                raise CheckoutValidationError(
                    f"Menu item {line.menu_item_id} is unavailable for this restaurant"
                )
            validated_items[item.id] = item

        return ValidatedCheckout(cart, restaurant, validated_items)

    def price(self, validated: ValidatedCheckout) -> CartView:
        """CHECKOUT-02: price a validated cart from the CURRENT menu data.

        validate() just read the menu items from the repository, and a cart line only stores
        an item ID and a quantity, so no earlier price is ever trusted.
        """
        return price_cart(validated.cart, validated.menu_items, validated.restaurant.delivery_fee)
    