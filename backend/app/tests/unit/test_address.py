import pytest
from unittest.mock import patch
from fastapi import HTTPException
from services.auth_service import register_user, build_user_response
from services.delivery_service import create_delivery
from services.orders_service import create_order, update_order
from schemas.auth import RegisterRequest, Role
from schemas.order import OrderCreate, OrderUpdate, OrderItem



def test_register_user_stores_address():
    payload = RegisterRequest(
        name="Alice",
        email="alice@example.com",
        password="password123",
        role="user",
        address="123 Main St",
    )
    with patch("services.auth_service.load_all_users", return_value=[]), \
         patch("services.auth_service.save_all_users") as mock_save:
        result = register_user(payload)
    assert result.address == "123 Main St"


def test_register_user_without_address():
    payload = RegisterRequest(
        name="Bob",
        email="bob@example.com",
        password="password123",
        role="user",
    )
    with patch("services.auth_service.load_all_users", return_value=[]), \
         patch("services.auth_service.save_all_users"):
        result = register_user(payload)
    assert result.address is None


def test_build_user_response_includes_address():
    user_dict = {
        "id": "u1",
        "name": "Carol",
        "email": "carol@example.com",
        "role": "user",
        "created_at": "2024-01-01T00:00:00Z",
        "address": "123 Main St",
    }
    result = build_user_response(user_dict)
    assert result.address == "123 Main St"


def test_build_user_response_missing_address_key():
    user_dict = {
        "id": "u2",
        "name": "Dave",
        "email": "dave@example.com",
        "role": "user",
        "created_at": "2024-01-01T00:00:00Z",
    }
    result = build_user_response(user_dict)
    assert result.address is None


def test_create_order_with_explicit_delivery_address():
    payload = OrderCreate(
        restaurant_id=1,
        customer_id="cust1",
        items=[OrderItem(food_item="Burger", quantity=1, unit_price=9.99)],
        delivery_address="456 Elm St",
    )
    with patch("services.orders_service.load_all", return_value=[]), \
         patch("services.orders_service.save_all"):
        result = create_order(payload)
    assert result.delivery_address == "456 Elm St"


def test_create_order_falls_back_to_user_address():
    payload = OrderCreate(
        restaurant_id=1,
        customer_id="cust2",
        items=[OrderItem(food_item="Pizza", quantity=1, unit_price=12.99)],
    )
    mock_users = [{"id": "cust2", "address": "789 Oak Ave"}]
    with patch("services.orders_service.load_all", return_value=[]), \
         patch("services.orders_service.save_all"), \
         patch("services.address_resolver.load_all_users", return_value=mock_users):
        result = create_order(payload)
    assert result.delivery_address == "789 Oak Ave"


def test_create_order_no_address_anywhere():
    payload = OrderCreate(
        restaurant_id=1,
        customer_id="cust3",
        items=[OrderItem(food_item="Salad", quantity=1, unit_price=7.99)],
    )
    mock_users = [{"id": "cust3"}]
    with patch("services.orders_service.load_all", return_value=[]), \
         patch("services.orders_service.save_all"), \
         patch("services.address_resolver.load_all_users", return_value=mock_users):
        result = create_order(payload)
    assert result.delivery_address is None


def test_update_order_preserves_delivery_address():
    existing_order = {
        "id": "order1",
        "restaurant_id": 1,
        "customer_id": "cust1",
        "items": [{"food_item": "Burger", "quantity": 1, "unit_price": 9.99}],
        "status": "draft",
        "created_at": "2024-01-01T00:00:00Z",
        "delivery_address": "123 Keep St",
    }
    payload = OrderUpdate(
        items=[OrderItem(food_item="Pasta", quantity=2, unit_price=11.50)],
    )
    with patch("services.orders_service.load_all", return_value=[existing_order]), \
         patch("services.orders_service.save_all"):
        result = update_order("order1", payload)
    assert result.delivery_address == "123 Keep St"


def test_create_delivery_autofills_dropoff_from_order():
    mock_orders = [{"id": "order1", "delivery_address": "456 Dropoff Ave", "restaurant_id": "1"}]
    mock_restaurants = [{"id": "1", "address": "123 Pickup St"}]
    with patch("services.address_resolver.load_all_orders", return_value=mock_orders), \
         patch("services.address_resolver.load_all_restaurants", return_value=mock_restaurants):
        result = create_delivery("order1")
    assert result.dropoff_address == "456 Dropoff Ave"


def test_create_delivery_autofills_pickup_from_restaurant():
    mock_orders = [{"id": "order1", "delivery_address": "456 Dropoff Ave", "restaurant_id": "1"}]
    mock_restaurants = [{"id": "1", "address": "123 Pickup St"}]
    with patch("services.address_resolver.load_all_orders", return_value=mock_orders), \
         patch("services.address_resolver.load_all_restaurants", return_value=mock_restaurants):
        result = create_delivery("order1")
    assert result.pickup_address == "123 Pickup St"


def test_create_delivery_explicit_addresses_not_overridden():
    mock_orders = [{"id": "order1", "delivery_address": "456 Dropoff Ave", "restaurant_id": "1"}]
    mock_restaurants = [{"id": "1", "address": "123 Pickup St"}]
    with patch("services.address_resolver.load_all_orders", return_value=mock_orders), \
         patch("services.address_resolver.load_all_restaurants", return_value=mock_restaurants):
        result = create_delivery("order1", pickup_address="Custom Pickup", dropoff_address="Custom Dropoff")
    assert result.pickup_address == "Custom Pickup"
    assert result.dropoff_address == "Custom Dropoff"