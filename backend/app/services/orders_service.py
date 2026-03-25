import uuid
from datetime import datetime, timezone
from typing import List, Optional, Tuple
from fastapi import HTTPException
from schemas.order import Order, OrderCreate, OrderUpdate, OrderStatus
from repositories.orders_repo import load_all, save_all
from repositories.users_repo import load_all as load_all_users


def _find_order(order_id: str) -> Tuple[int, dict, list]:
    orders = load_all()
    for idx, o in enumerate(orders):
        if o.get("id") == order_id:
            return idx, o, orders
    raise HTTPException(status_code=404, detail=f"Order '{order_id}' not found")


def _require_draft(order: dict, action: str) -> None:
    if order.get("status") != OrderStatus.DRAFT.value:
        raise HTTPException(status_code=400, detail=f"Only draft orders can be {action}.")


def list_orders(customer_id: Optional[str] = None, status: Optional[OrderStatus] = None) -> List[Order]:
    orders = load_all()
    if customer_id:
        orders = [o for o in orders if o.get("customer_id") == customer_id]
    if status:
        orders = [o for o in orders if o.get("status") == status.value]
    return [Order(**o) for o in orders]


def create_order(payload: OrderCreate) -> Order:
    orders = load_all()
    new_id = str(uuid.uuid4())
    if any(o.get("id") == new_id for o in orders):
        raise HTTPException(status_code=409, detail="ID collision; retry.")
    delivery_address = payload.delivery_address
    if not delivery_address:
        users = load_all_users()
        user = next((u for u in users if u["id"] == payload.customer_id), None)
        if user:
            delivery_address = user.get("address")
    new_order = Order(
        id=new_id,
        restaurant_id=payload.restaurant_id,
        customer_id=payload.customer_id.strip(),
        items=payload.items,
        status=OrderStatus.DRAFT,
        created_at=datetime.now(timezone.utc).isoformat(),
        delivery_address=delivery_address,
    )
    orders.append(new_order.model_dump())
    save_all(orders)
    return new_order


def get_order_by_id(order_id: str) -> Order:
    _, order, _ = _find_order(order_id)
    return Order(**order)


def update_order(order_id: str, payload: OrderUpdate) -> Order:
    orders = load_all()
    for idx, o in enumerate(orders):
        if o.get("id") == order_id:
            if o.get("status") != OrderStatus.DRAFT.value:
                raise HTTPException(
                    status_code=400,
                    detail="Only draft orders can be modified.",
                )
            updated = Order(
                id=order_id,
                restaurant_id=o["restaurant_id"],
                customer_id=o["customer_id"],
                items=payload.items,
                status=OrderStatus.DRAFT,
                created_at=o["created_at"],
                delivery_address=o.get("delivery_address"),
            )
            orders[idx] = updated.model_dump()
            save_all(orders)
            return updated
    raise HTTPException(status_code=404, detail=f"Order '{order_id}' not found")


def confirm_order(order_id: str) -> Order:
    idx, o, orders = _find_order(order_id)
    _require_draft(o, "confirmed")
    confirmed = Order(
        id=order_id,
        restaurant_id=o["restaurant_id"],
        customer_id=o["customer_id"],
        items=[item for item in o["items"]],
        status=OrderStatus.CONFIRMED,
        created_at=o["created_at"],
        confirmed_at=datetime.now(timezone.utc).isoformat(),
    )
    orders[idx] = confirmed.model_dump()
    save_all(orders)
    return confirmed


def cancel_order(order_id: str) -> None:
    idx, o, orders = _find_order(order_id)
    _require_draft(o, "cancelled")
    cancelled = Order(
        id=order_id,
        restaurant_id=o["restaurant_id"],
        customer_id=o["customer_id"],
        items=[item for item in o["items"]],
        status=OrderStatus.CANCELLED,
        created_at=o["created_at"],
    )
    orders[idx] = cancelled.model_dump()
    save_all(orders)
