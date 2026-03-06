import logging
import uuid
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import HTTPException
from app.schemas.order import Order, OrderCreate, OrderUpdate, OrderStatus
from app.repositories.orders_repo import load_all, save_all

logger = logging.getLogger(__name__)


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
    new_order = Order(
        id=new_id,
        restaurant_id=payload.restaurant_id,
        customer_id=payload.customer_id.strip(),
        items=payload.items,
        status=OrderStatus.DRAFT,
        created_at=datetime.now(timezone.utc).isoformat(),
    )
    orders.append(new_order.dict())
    save_all(orders)
    logger.info("order_created id=%s customer=%s restaurant=%d", new_id, payload.customer_id, payload.restaurant_id)
    return new_order


def get_order_by_id(order_id: str) -> Order:
    for o in load_all():
        if o.get("id") == order_id:
            return Order(**o)
    raise HTTPException(status_code=404, detail=f"Order '{order_id}' not found")


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
            )
            orders[idx] = updated.dict()
            save_all(orders)
            return updated
    raise HTTPException(status_code=404, detail=f"Order '{order_id}' not found")


def confirm_order(order_id: str) -> Order:
    orders = load_all()
    for idx, o in enumerate(orders):
        if o.get("id") == order_id:
            if o.get("status") != OrderStatus.DRAFT.value:
                raise HTTPException(
                    status_code=400,
                    detail="Only draft orders can be confirmed.",
                )
            o["status"] = OrderStatus.CONFIRMED.value
            o["confirmed_at"] = datetime.now(timezone.utc).isoformat()
            orders[idx] = o
            save_all(orders)
            logger.info("order_confirmed id=%s", order_id)
            return Order(**o)
    raise HTTPException(status_code=404, detail=f"Order '{order_id}' not found")


def cancel_order(order_id: str) -> None:
    orders = load_all()
    for idx, o in enumerate(orders):
        if o.get("id") == order_id:
            if o.get("status") != OrderStatus.DRAFT.value:
                raise HTTPException(
                    status_code=400,
                    detail="Only draft orders can be cancelled.",
                )
            o["status"] = OrderStatus.CANCELLED.value
            orders[idx] = o
            save_all(orders)
            return
    raise HTTPException(status_code=404, detail=f"Order '{order_id}' not found")
