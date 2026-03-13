from decimal import Decimal
from services.tax_calculator import get_tax_rate, calculate_tax, calculate_money

def test_get_tax_rate_valid_province():
    assert get_tax_rate("BC") == Decimal("0.12")
    assert get_tax_rate("ON") == Decimal("0.13")

def test_get_tax_rate_strips_and_case_sensitive():
    assert get_tax_rate(" bc ") == Decimal("0.12")
    assert get_tax_rate("on") == Decimal("0.13")

def test_calculate_money_rounds_half_up():
    assert calculate_money(Decimal("10.005")) == Decimal("10.01")
    assert calculate_money(Decimal("10.004")) == Decimal("10.00")

def test_calculate_tax_for_bc():
    tax_rate, tax = calculate_tax(Decimal("10.00"), "BC")
    assert tax_rate == Decimal("0.12")
    assert tax == Decimal("1.20")
