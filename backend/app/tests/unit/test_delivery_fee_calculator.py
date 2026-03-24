from decimal import Decimal
from services.delivery_fee_calculator import calculate_delivery_fee

def test_delivery_fee_normal_distance():
    assert calculate_delivery_fee(Decimal("4")) == Decimal("2.99")  # 0.99 + 0.50*4 (delivery fee rule)

def test_delivery_fee_zero_distance():
    assert calculate_delivery_fee(Decimal("0")) == Decimal("0.99") 

def test_delivery_fee_capped():
    assert calculate_delivery_fee(Decimal("20")) == Decimal("6.99")  # capped at 6.99

def test_delivery_fee_rounding():
    assert calculate_delivery_fee(Decimal("1.11")) == Decimal("1.55")  # 0.99 + 0.50*1.11 = 1.545 rounded to 1.55