from fastapi import APIRouter
from decimal import Decimal
from schemas.order_total import OrderTotalResponse
from services.order_total_calculator import calculate_order_total
from services.orders_service import get_order_by_id

router = APIRouter(prefix="/orders", tags=["order-total"])

@router.get("/{order_id}/total", response_model=OrderTotalResponse)
def get_order_total(order_id: str, province: str, distance_km: Decimal):
    order = get_order_by_id(order_id)
    subtotal, tax_rate, tax, delivery_fee, total = calculate_order_total(
        order = order,
        province = province,
        distance_km = distance_km
    )
    return OrderTotalResponse(
        order_id = order_id,
        subtotal = subtotal,
        tax_rate = tax_rate,
        tax = tax,
        delivery_fee = delivery_fee,
        total = total,
    )
