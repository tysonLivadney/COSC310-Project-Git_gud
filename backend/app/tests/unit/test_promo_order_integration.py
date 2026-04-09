from fastapi.testclient import TestClient
from repositories.orders_repo import load_all as load_orders, save_all as save_orders
from repositories.promo_codes_repo import load_all as load_promos, save_all as save_promos
from repositories.users_repo import load_all as load_users, save_all as save_users
from repositories.sessions_repo import load_all as load_sessions, save_all as save_sessions
from unittest.mock import patch, MagicMock
import pytest
from main import app

client = TestClient(app)

MANAGER_USER = {
    "name": "Promo Manager",
    "email": "promomanager@test.com",
    "password": "password123",
    "role": "manager",
}

SAMPLE_ORDER = {
    "restaurant_id": "1",
    "customer_id": "customer-1",
    "items": [{"food_item": "Burger", "quantity": 2, "unit_price": 10.00}],
    "delivery_address": "123 Test St",
}

PAYMENT_INFO = {
    "card_number": "4242424242424242",
    "expiry": "12/26",
    "cvv": "805",
}


@pytest.fixture(autouse=True)
def mock_restaurant_hours():
    mock_restaurant = MagicMock()
    with patch("services.orders_service.can_accept_order", return_value=True),\
        patch("services.orders_service.get_restaurant_by_id", return_value=mock_restaurant):
            yield


@pytest.fixture(autouse=True)
def save_and_restore():
    orders = load_orders()
    promos = load_promos()
    users = load_users()
    sessions = load_sessions()
    save_orders([])
    save_promos([])
    save_users([])
    save_sessions([])
    yield
    save_orders(orders)
    save_promos(promos)
    save_users(users)
    save_sessions(sessions)


def get_manager_token():
    client.post("/auth/register", json=MANAGER_USER)
    resp = client.post("/auth/login", json={
        "email": MANAGER_USER["email"],
        "password": MANAGER_USER["password"],
    })
    return resp.json()["token"]


def create_promo(token, code="SAVE20", discount_type="percentage", discount_value=20, **kwargs):
    payload = {
        "code": code,
        "discount_type": discount_type,
        "discount_value": discount_value,
        **kwargs,
    }
    client.post("/promo-codes", json=payload, headers={"Authorization": f"Bearer {token}"})


def test_confirm_order_with_percentage_promo():
    token = get_manager_token()
    create_promo(token, "TWENTY", "percentage", 20)

    order = client.post("/orders", json=SAMPLE_ORDER).json()
    resp = client.post(f"/orders/{order['id']}/confirm", json={
        "payment_info": PAYMENT_INFO,
        "promo_code": "TWENTY",
    })

    assert resp.status_code == 200
    data = resp.json()
    # subtotal is 20.00 (2 burgers at 10), 20% off = 4.00 discount
    assert float(data["discount"]) == 4.00


def test_confirm_order_with_flat_promo():
    token = get_manager_token()
    create_promo(token, "FIVE", "flat", 5)

    order = client.post("/orders", json=SAMPLE_ORDER).json()
    resp = client.post(f"/orders/{order['id']}/confirm", json={
        "payment_info": PAYMENT_INFO,
        "promo_code": "FIVE",
    })

    assert resp.status_code == 200
    data = resp.json()
    assert float(data["discount"]) == 5.00


def test_confirm_order_without_promo():
    order = client.post("/orders", json=SAMPLE_ORDER).json()
    resp = client.post(f"/orders/{order['id']}/confirm", json={
        "payment_info": PAYMENT_INFO,
    })

    assert resp.status_code == 200
    data = resp.json()
    assert float(data["discount"]) == 0.00


def test_promo_usage_increments_after_confirm():
    token = get_manager_token()
    create_promo(token, "USEONCE", "flat", 3)

    order = client.post("/orders", json=SAMPLE_ORDER).json()
    client.post(f"/orders/{order['id']}/confirm", json={
        "payment_info": PAYMENT_INFO,
        "promo_code": "USEONCE",
    })

    promos = load_promos()
    for p in promos:
        if p["code"] == "USEONCE":
            assert p["usage_count"] == 1


def test_promo_code_saved_on_order():
    token = get_manager_token()
    create_promo(token, "SAVED", "flat", 2)

    order = client.post("/orders", json=SAMPLE_ORDER).json()
    client.post(f"/orders/{order['id']}/confirm", json={
        "payment_info": PAYMENT_INFO,
        "promo_code": "SAVED",
    })

    resp = client.get(f"/orders/{order['id']}")
    data = resp.json()
    assert data["promo_code"] == "SAVED"
    assert data["discount"] == "2.00"


def test_confirm_with_invalid_promo_fails():
    order = client.post("/orders", json=SAMPLE_ORDER).json()
    resp = client.post(f"/orders/{order['id']}/confirm", json={
        "payment_info": PAYMENT_INFO,
        "promo_code": "DOESNTEXIST",
    })

    assert resp.status_code == 404


def test_confirm_with_expired_promo_fails():
    token = get_manager_token()
    create_promo(token, "OLD", "flat", 5, expiry_date="2020-01-01T00:00:00")

    order = client.post("/orders", json=SAMPLE_ORDER).json()
    resp = client.post(f"/orders/{order['id']}/confirm", json={
        "payment_info": PAYMENT_INFO,
        "promo_code": "OLD",
    })

    assert resp.status_code == 400


def test_confirm_with_below_min_order_promo_fails():
    token = get_manager_token()
    create_promo(token, "BIG", "percentage", 10, min_order_amount=100.00)

    # order subtotal is only 20.00
    order = client.post("/orders", json=SAMPLE_ORDER).json()
    resp = client.post(f"/orders/{order['id']}/confirm", json={
        "payment_info": PAYMENT_INFO,
        "promo_code": "BIG",
    })

    assert resp.status_code == 400
