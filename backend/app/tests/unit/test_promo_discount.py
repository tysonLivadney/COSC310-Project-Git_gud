from decimal import Decimal
import pytest
from schemas.promo_code import PromoCode, DiscountType
from services.promo_code_service import calculate_discount


def make_promo(discount_type, discount_value):
    return PromoCode(
        id="test-id",
        code="TEST",
        discount_type=discount_type,
        discount_value=discount_value,
        usage_count=0,
        active=True,
        created_at="2026-01-01T00:00:00",
    )


def test_percentage_discount():
    promo = make_promo(DiscountType.PERCENTAGE, 20)
    result = calculate_discount(promo, Decimal("100.00"))
    assert result == Decimal("20.00")


def test_percentage_discount_rounds_properly():
    promo = make_promo(DiscountType.PERCENTAGE, 15)
    result = calculate_discount(promo, Decimal("33.33"))
    # 33.33 * 0.15 = 4.9995, should round to 5.00
    assert result == Decimal("5.00")


def test_flat_discount():
    promo = make_promo(DiscountType.FLAT, 10)
    result = calculate_discount(promo, Decimal("50.00"))
    assert result == Decimal("10.00")


def test_flat_discount_capped_at_subtotal():
    # discount shouldnt be more than the subtotal
    promo = make_promo(DiscountType.FLAT, 100)
    result = calculate_discount(promo, Decimal("25.00"))
    assert result == Decimal("25.00")


def test_percentage_discount_capped_at_subtotal():
    # 200% off shouldnt go negative
    promo = make_promo(DiscountType.PERCENTAGE, 200)
    result = calculate_discount(promo, Decimal("30.00"))
    assert result == Decimal("30.00")


def test_small_percentage_discount():
    promo = make_promo(DiscountType.PERCENTAGE, 5)
    result = calculate_discount(promo, Decimal("10.00"))
    assert result == Decimal("0.50")


def test_flat_discount_exact_match():
    promo = make_promo(DiscountType.FLAT, 50)
    result = calculate_discount(promo, Decimal("50.00"))
    assert result == Decimal("50.00")


def test_zero_subtotal():
    promo = make_promo(DiscountType.FLAT, 10)
    result = calculate_discount(promo, Decimal("0.00"))
    assert result == Decimal("0.00")
