from typing import List, Optional
from datetime import datetime
from schemas.order import Order, OrderStatus
from schemas.admin import AdminReport, RestaurantRevenue
from schemas.delivery import DeliveryStatus
from repositories.orders_repo import load_all
from repositories.delivery_repo import load_all as load_all_deliveries
from repositories.reviews_repo import load_all as load_all_reviews


def _filter_by_date_range(orders: list, date_from: Optional[str], date_to: Optional[str]) -> list:
    if date_from:
        orders = [o for o in orders if o.get("created_at", "") >= date_from]
    if date_to:
        orders = [o for o in orders if o.get("created_at", "") <= date_to]
    return orders


def _calculate_order_revenue(order: dict) -> float:
    return sum(
        item.get("quantity", 0) * item.get("unit_price", 0)
        for item in order.get("items", [])
    )


def list_all_orders(
    customer_id: Optional[str] = None,
    restaurant_id: Optional[int] = None,
    status: Optional[OrderStatus] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
) -> List[Order]:
    orders = load_all()

    if customer_id:
        orders = [o for o in orders if o.get("customer_id") == customer_id]
    if restaurant_id is not None:
        orders = [o for o in orders if o.get("restaurant_id") == restaurant_id]
    if status:
        orders = [o for o in orders if o.get("status") == status.value]

    orders = _filter_by_date_range(orders, date_from, date_to)

    return [Order(**o) for o in orders]


def generate_report(
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
) -> AdminReport:
    orders = load_all()

    billable = [
        o for o in orders
        if o.get("status") in (OrderStatus.CONFIRMED.value, OrderStatus.COMPLETED.value)
    ]

    billable = _filter_by_date_range(billable, date_from, date_to)

    total_revenue = 0.0
    restaurant_map = {}

    for o in billable:
        order_total = _calculate_order_revenue(o)
        total_revenue += order_total

        rid = o.get("restaurant_id")
        if rid not in restaurant_map:
            restaurant_map[rid] = {"total_revenue": 0.0, "order_count": 0}
        restaurant_map[rid]["total_revenue"] += order_total
        restaurant_map[rid]["order_count"] += 1

    revenue_per_restaurant = [
        RestaurantRevenue(
            restaurant_id=rid,
            total_revenue=round(data["total_revenue"], 2),
            order_count=data["order_count"],
        )
        for rid, data in sorted(restaurant_map.items(), key=lambda x: x[1]["total_revenue"], reverse=True)
    ]

    avg_delivery_time = _calculate_avg_delivery_time()
    top_restaurants = _get_highest_rated_restaurants()

    return AdminReport(
        total_revenue=round(total_revenue, 2),
        revenue_per_restaurant=revenue_per_restaurant,
        average_delivery_time=avg_delivery_time,
        highest_rated_restaurants=top_restaurants,
    )


def _calculate_avg_delivery_time() -> Optional[float]:
    deliveries = load_all_deliveries()

    completed = [
        d for d in deliveries
        if d.get("status") == DeliveryStatus.DELIVERED.value
    ]

    if not completed:
        return None

    total_minutes = 0.0
    for d in completed:
        created = datetime.fromisoformat(d["created_at"])
        updated = datetime.fromisoformat(d["updated_at"])
        diff = (updated - created).total_seconds() / 60
        total_minutes += diff

    return round(total_minutes / len(completed), 2)


def _get_highest_rated_restaurants(limit: int = 5) -> List[int]:
    reviews = load_all_reviews()

    if not reviews:
        return []

    rating_map = {}
    for r in reviews:
        rid = r.get("restaurant_id")
        if rid not in rating_map:
            rating_map[rid] = []
        rating_map[rid].append(r.get("rating", 0))

    averages = []
    for rid, ratings in rating_map.items():
        avg = sum(ratings) / len(ratings)
        averages.append((rid, avg))

    averages.sort(key=lambda x: x[1], reverse=True)

    return [rid for rid, avg in averages[:limit]]
