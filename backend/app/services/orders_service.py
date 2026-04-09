import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Optional, Tuple

from fastapi import HTTPException

from schemas.order import Order, OrderCreate, OrderUpdate, OrderStatus
from schemas.payment import PaymentInfo, PaymentProcessRequest
from repositories.orders_repo import load_all, save_all
from services.address_resolver import resolve_customer_address
from services.location_service import LocationService
from services.order_total_calculator import OrderTotalService, subtotal_from_order
from services.payment_service import PaymentService
from services.restaurants_service import can_accept_order, get_restaurant_by_id
from services.promo_code_service import validate_promo_code, calculate_discount, increment_usage


def validate_user_state(payload: OrderCreate) -> None:
    customer_id = payload.customer_id.strip()

    if customer_id.startswith("guest-"):
        if not payload.delivery_address or not payload.delivery_address.strip():
            raise HTTPException(
                status_code=400,
                detail="Guest checkout requires a delivery address."
            )


def validate_order_before_confirm(order: Order) -> None:
    if not order.items:
        raise HTTPException(status_code=400, detail="Order must contain at least one item.")
    if not order.delivery_address or not order.delivery_address.strip():
        raise HTTPException(status_code=400, detail="Delivery address is required before checkout.")


def _find_order(order_id: str) -> Tuple[int, dict, list]:
    orders = load_all()
    for idx, o in enumerate(orders):
        if o.get("id") == order_id:
            return idx, o, orders
    raise HTTPException(status_code=404, detail=f"Order '{order_id}' not found")


def _require_draft(order: dict, action: str) -> None:
    if order.get("status") != OrderStatus.DRAFT.value:
        raise HTTPException(status_code=400, detail=f"Only draft orders can be {action}.")


location_service = LocationService()


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

    validate_user_state(payload)

    restaurant = get_restaurant_by_id(payload.restaurant_id)
    if restaurant is None:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    
    if not can_accept_order(restaurant):
        raise HTTPException(
            status_code=400,
            detail="Restaurant is closed or cannot complete order in time"
        )

    delivery_address = resolve_customer_address(payload.customer_id, payload.delivery_address)

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
    for o in load_all():
        if o.get("id") == order_id:
            return Order(**o)
    raise HTTPException(status_code=404, detail=f"Order '{order_id}' not found")


def update_order(order_id: str, payload: OrderUpdate) -> Order:
    idx, o, orders = _find_order(order_id)
    _require_draft(o, "modified")

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


def _calculate_and_process_payment(order, order_id, payment_info, discount=Decimal("0.00")):
    customer_location = location_service.get_user_location(order.customer_id)
    restaurant_location = location_service.get_restaurant_location(order.restaurant_id)

    if customer_location is None or restaurant_location is None:
        distance_km = Decimal("1.0")
    else:
        distance_km = Decimal(
            str(location_service.calculate_distance_between(customer_location, restaurant_location))
        )

    province = "BC"
    subtotal, tax_rate, tax, delivery_fee, total = OrderTotalService.calculate_order_total(
        order, province, distance_km,
    )

    # apply promo code discount to the total
    total = total - discount
    if total < Decimal("0.00"):
        total = Decimal("0.00")

    payment_request = PaymentProcessRequest(
        order_id=order_id, total=total, payment_info=payment_info,
    )
    payment_result = PaymentService.process_payment(payment_request)

    return {
        "payment": payment_result,
        "distance_km": float(distance_km),
        "subtotal": subtotal, "tax_rate": tax_rate,
        "tax": tax, "delivery_fee": delivery_fee,
        "discount": discount, "total": total, "province": province,
    }


def confirm_order(order_id: str, payment_info: PaymentInfo, promo_code: str = None):
    idx, o, orders = _find_order(order_id)
    _require_draft(o, "confirmed")

    order = Order(**o)
    validate_order_before_confirm(order)

    restaurant = get_restaurant_by_id(order.restaurant_id)
    if not can_accept_order(restaurant):
        raise HTTPException(status_code=400, detail="Restaurant is closed or cannot complete order in time")

    # if a promo code was provided, validate it against the subtotal
    discount_amount = Decimal("0.00")
    applied_promo = None
    if promo_code:
        subtotal = OrderTotalService.subtotal_from_order(order)
        promo = validate_promo_code(promo_code, float(subtotal))
        discount_amount = calculate_discount(promo, subtotal)
        applied_promo = promo_code.strip().upper()

    pricing = _calculate_and_process_payment(order, order_id, payment_info, discount_amount)

    # if promo was used, increment the usage count
    if applied_promo:
        increment_usage(applied_promo)

    o["status"] = OrderStatus.CONFIRMED.value
    o["confirmed_at"] = datetime.now(timezone.utc).isoformat()
    o["subtotal"] = str(pricing["subtotal"])
    o["tax"] = str(pricing["tax"])
    o["delivery_fee"] = str(pricing["delivery_fee"])
    o["total"] = str(pricing["total"])
    if applied_promo:
        o["promo_code"] = applied_promo
        o["discount"] = str(discount_amount)

    orders[idx] = o
    save_all(orders)

    return {
        "order_id": o["id"],
        "status": o["status"],
        "confirmed_at": o["confirmed_at"],
        **pricing,
    }


def complete_order(order_id: str) -> None:
    idx, o, orders = _find_order(order_id)
    if o.get("status") != OrderStatus.CONFIRMED.value:
        raise HTTPException(status_code=400, detail="Only confirmed orders can be completed.")
    o["status"] = OrderStatus.COMPLETED.value
    orders[idx] = o
    save_all(orders)


def cancel_order(order_id: str) -> None:
    orders = load_all()

    for idx, o in enumerate(orders):
        if o.get("id") == order_id:
            if o.get("status") not in [OrderStatus.DRAFT.value, OrderStatus.CONFIRMED.value]:
                raise HTTPException(
                    status_code=400,
                    detail="Only draft or confirmed orders can be cancelled.",
                )

            o["status"] = OrderStatus.CANCELLED.value
            o["cancelled_at"] = datetime.now(timezone.utc).isoformat()
            orders[idx] = o
            save_all(orders)

            if o.get("confirmed_at"):
                refund_order(order_id)

            return

    raise HTTPException(status_code=404, detail=f"Order '{order_id}' not found")


def refund_order(order_id: str) -> Order:
    orders = load_all()
    for idx, o in enumerate(orders):
        if o.get("id") == order_id:
            if o.get("status") != OrderStatus.CANCELLED.value:
                raise HTTPException(
                    status_code=400,
                    detail="Only cancelled orders can be refunded.",
                )

            order = Order(**o)
            refund_amount = subtotal_from_order(order)
            o["status"] = OrderStatus.REFUNDED.value
            o["refunded_at"] = datetime.now(timezone.utc).isoformat()
            o["refund_amount"] = str(refund_amount)
            orders[idx] = o
            save_all(orders)
            return Order(**o)

    raise HTTPException(status_code=404, detail=f"Order '{order_id}' not found")