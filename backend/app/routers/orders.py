from fastapi import APIRouter, status as http_status
from typing import List, Optional
from schemas.order import Order, OrderCreate, OrderUpdate, OrderStatus
from services.orders_service import (
    list_orders,
    create_order,
    get_order_by_id,
    update_order,
    confirm_order,
    cancel_order,
)

router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("", response_model=List[Order])
def get_orders(customer_id: Optional[str] = None, order_status: Optional[OrderStatus] = None):
    return list_orders(customer_id=customer_id, status=order_status)


@router.post("", response_model=Order, status_code=201)
def post_order(payload: OrderCreate):
    return create_order(payload)


@router.get("/{order_id}", response_model=Order)
def get_order(order_id: str):
    return get_order_by_id(order_id)


@router.put("/{order_id}", response_model=Order)
def put_order(order_id: str, payload: OrderUpdate):
    return update_order(order_id, payload)


@router.post("/{order_id}/confirm", response_model=Order)
def post_confirm_order(order_id: str):
    return confirm_order(order_id)


@router.delete("/{order_id}", status_code=http_status.HTTP_204_NO_CONTENT)
def delete_order(order_id: str):
    cancel_order(order_id)
    return None
