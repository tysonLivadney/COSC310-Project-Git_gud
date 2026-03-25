from typing import List, Optional
from schemas.order import Order, OrderStatus
from schemas.admin import AdminReport, RestaurantRevenue
from repositories.orders_repo import load_all


def list_all_orders(
    customer_id: Optional[str] = None,
    restaurant_id: Optional[str] = None,
    status: Optional[OrderStatus] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
) -> List[Order]:
    orders = load_all()

    if customer_id:
        orders = [o for o in orders if o.get("customer_id") == str(customer_id)]
    if restaurant_id is not None:
        orders = [o for o in orders if o.get("restaurant_id") == str(restaurant_id)]
    if status:
        orders = [o for o in orders if o.get("status") == status.value]
    if date_from:
        orders = [o for o in orders if o.get("created_at", "") >= date_from]
    if date_to:
        orders = [o for o in orders if o.get("created_at", "") <= date_to]

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

    if date_from:
        billable = [o for o in billable if o.get("created_at", "") >= date_from]
    if date_to:
        billable = [o for o in billable if o.get("created_at", "") <= date_to]

    total_revenue = 0.0
    restaurant_map = {}

    for o in billable:
        order_total = sum(
            item.get("quantity", 0) * item.get("unit_price", 0)
            for item in o.get("items", [])
        )
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

    return AdminReport(
        total_revenue=round(total_revenue, 2),
        revenue_per_restaurant=revenue_per_restaurant,
    )
