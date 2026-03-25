from decimal import Decimal, ROUND_HALF_UP
from schemas.order import Order
from services.tax_calculator import calculate_tax, calculate_money
from services.delivery_fee_calculator import calculate_delivery_fee

two_places = Decimal('0.01')
def subtotal_from_order(order: Order) -> Decimal:
    subtotal = Decimal("0.00")
    for item in order.items:
        unit_price = Decimal(str(item.unit_price))
        subtotal += unit_price * item.quantity
    return subtotal.quantize(two_places, rounding=ROUND_HALF_UP)

def calculate_order_total(order: Order, province: str, distance_km: Decimal):
    sub = subtotal_from_order(order)
    delivery_fee = calculate_delivery_fee(distance_km)
    tax_amount = calculate_money(sub + delivery_fee)
    tax_rate, tax = calculate_tax(tax_amount, province)
    total = calculate_money(sub + delivery_fee + tax)
    return sub, tax_rate, tax, delivery_fee, total