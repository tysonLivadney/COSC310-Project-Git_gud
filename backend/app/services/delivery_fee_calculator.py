from decimal import Decimal, ROUND_HALF_UP
from services.tax_calculator import calculate_money

def calculate_delivery_fee(distance: Decimal) -> Decimal:
    base = Decimal("0.99")
    per_km = Decimal("0.50")
    cap = Decimal("6.99")
    if distance < 0:
        distance = Decimal("0")
    fee = base + per_km * distance
    if fee > cap:
        fee = cap
    return calculate_money(fee)