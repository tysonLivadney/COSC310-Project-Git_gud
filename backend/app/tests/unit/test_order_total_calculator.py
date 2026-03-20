from decimal import Decimal
from schemas.order import Order, OrderItem
from services.order_total_calculator import subtotal_from_order, calculate_order_total
from datetime import datetime

def make_order():
    return Order(
        id="order-1",
        restaurant_id=1,
        customer_id="cust-1",
        items=[
            OrderItem(food_item="Burger", quantity=2, unit_price=9.99),
            OrderItem(food_item="Fries", quantity=2, unit_price=3.50),
        ],
        created_at=datetime.now().isoformat()
    )

def test_subtotal_calculation():
    order = make_order()
    assert subtotal_from_order(order) == Decimal("26.98")  # (2*9.99) + (2*3.50)

def test_calculate_order_total_in_BC():
    order = make_order()
    sub, tax_rate, tax, delivery_fee, total = calculate_order_total(
        order, 
        "BC", 
        Decimal("4")
    )
    # subtotal = 26.98
    # delivery fee = 0.99 + 0.50*4 = 2.99
    # tax amount = 26.98 + 2.99 = 29.97
    # tax = 29.97 * 0.12 = 3.60
    # total = 26.98 + 2.99 + 3.60 = 33.57
    assert sub == Decimal("26.98")
    assert tax_rate == Decimal("0.12")
    assert tax == Decimal("3.60")
    assert delivery_fee == Decimal("2.99")
    assert total == Decimal("33.57")
