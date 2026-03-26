from typing import Optional
from repositories.users_repo import load_all as load_all_users
from repositories.orders_repo import load_all as load_all_orders
from repositories.restaurants_repo import load_all as load_all_restaurants


def resolve_customer_address(customer_id: str, provided_address: Optional[str]) -> Optional[str]:
    if provided_address:
        return provided_address
    users = load_all_users()
    user = next((u for u in users if u["id"] == customer_id), None)
    if user:
        return user.get("address")
    return None


def resolve_delivery_addresses(
    order_id: str,
    pickup_address: Optional[str],
    dropoff_address: Optional[str],
) -> tuple[Optional[str], Optional[str]]:
    if pickup_address and dropoff_address:
        return pickup_address, dropoff_address
    orders = load_all_orders()
    order = next((o for o in orders if o.get("id") == order_id), None)
    if order:
        if not dropoff_address:
            dropoff_address = order.get("delivery_address")
        if not pickup_address:
            restaurants = load_all_restaurants()
            restaurant = next(
                (r for r in restaurants if str(r.get("id")) == str(order.get("restaurant_id"))),
                None,
            )
            if restaurant:
                pickup_address = restaurant.get("address")
    return pickup_address, dropoff_address
