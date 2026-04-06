from fastapi.testclient import TestClient
from repositories.orders_repo import load_all as load_orders, save_all as save_orders
from unittest.mock import patch, MagicMock
import pytest
from main import app

client = TestClient(app)

@pytest.fixture(autouse=True)
def mock_restaurant_hours():
    mock_restaurant = MagicMock()
    with patch("services.orders_service.can_accept_order", return_value=True),\
        patch("services.orders_service.get_restaurant_by_id", return_value=mock_restaurant):
            yield

TEST_PAYLOAD = {
    "payment_info": {
        "card_number": "4242424242424242",
        "expiry": "12/26",
        "cvv": "805"
    }
}

SAMPLE_ORDER = {
    "restaurant_id": "1",
    "customer_id": "customer-1",
    "items": [{"food_item": "Burger", "quantity": 2, "unit_price": 10.00}],
}

SAMPLE_ORDER_2 = {
    "restaurant_id": "2",
    "customer_id": "customer-2",
    "items": [{"food_item": "Pizza", "quantity": 1, "unit_price": 15.00}],
}


@pytest.fixture(autouse=True)
def save_and_restore():
    orders = load_orders()
    save_orders([])
    yield
    save_orders(orders)


#POST /orders tests
def test_create_order():
    response = client.post("/orders", json=SAMPLE_ORDER)
    assert response.status_code == 201
    data = response.json()
    assert data["restaurant_id"] == "1"
    assert data["customer_id"] == "customer-1"
    assert data["status"] == "draft"
    assert len(data["items"]) == 1
    assert data["items"][0]["food_item"] == "Burger"


def test_create_order_has_id():
    response = client.post("/orders", json=SAMPLE_ORDER)
    assert response.status_code == 201
    assert "id" in response.json()
    assert len(response.json()["id"]) > 0


def test_create_order_missing_items():
    response = client.post("/orders", json={
        "restaurant_id": "1",
        "customer_id": "customer-1",
        "items": [],
    })
    assert response.status_code == 422


def test_create_order_missing_fields():
    response = client.post("/orders", json={"restaurant_id": "1"})
    assert response.status_code == 422


#GET /orders tests
def test_list_orders_empty():
    response = client.get("/orders")
    assert response.status_code == 200
    assert response.json() == []


def test_list_orders():
    client.post("/orders", json=SAMPLE_ORDER)
    client.post("/orders", json=SAMPLE_ORDER_2)
    response = client.get("/orders")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_filter_orders_by_customer():
    client.post("/orders", json=SAMPLE_ORDER)
    client.post("/orders", json=SAMPLE_ORDER_2)
    response = client.get("/orders", params={"customer_id": "customer-1"})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["customer_id"] == "customer-1"


def test_filter_orders_by_status():
    order = client.post("/orders", json=SAMPLE_ORDER).json()
    client.post(f"/orders/{order['id']}/confirm", json=TEST_PAYLOAD)
    client.post("/orders", json=SAMPLE_ORDER_2)

    response = client.get("/orders", params={"status": "confirmed"})
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["status"] == "confirmed"


#GET /orders/{id} tests
def test_get_order_by_id():
    order = client.post("/orders", json=SAMPLE_ORDER).json()
    response = client.get(f"/orders/{order['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == order["id"]


def test_get_order_not_found():
    response = client.get("/orders/nonexistent-id")
    assert response.status_code == 404


#PUT /orders/{id} tests
def test_update_order_items():
    order = client.post("/orders", json=SAMPLE_ORDER).json()
    new_items = [{"food_item": "Fries", "quantity": 3, "unit_price": 5.00}]
    response = client.put(f"/orders/{order['id']}", json={"items": new_items})
    assert response.status_code == 200
    assert response.json()["items"][0]["food_item"] == "Fries"
    assert response.json()["restaurant_id"] == "1"


def test_update_keeps_original_customer():
    order = client.post("/orders", json=SAMPLE_ORDER).json()
    new_items = [{"food_item": "Salad", "quantity": 1, "unit_price": 8.00}]
    response = client.put(f"/orders/{order['id']}", json={"items": new_items})
    assert response.status_code == 200
    assert response.json()["customer_id"] == "customer-1"


def test_update_confirmed_order_fails():
    order = client.post("/orders", json=SAMPLE_ORDER).json()
    client.post(f"/orders/{order['id']}/confirm", json=TEST_PAYLOAD)
    new_items = [{"food_item": "Fries", "quantity": 1, "unit_price": 5.00}]
    response = client.put(f"/orders/{order['id']}", json={"items": new_items})
    assert response.status_code == 400


def test_update_nonexistent_order():
    response = client.put("/orders/fake-id", json={
        "items": [{"food_item": "Burger", "quantity": 1, "unit_price": 10.00}],
    })
    assert response.status_code == 404


#POST /orders/{id}/confirm tests
def test_confirm_order():
    order = client.post("/orders", json=SAMPLE_ORDER).json()
    response = client.post(f"/orders/{order['id']}/confirm", json=TEST_PAYLOAD)
    assert response.status_code == 200
    assert response.json()["status"] == "confirmed"
    assert response.json()["confirmed_at"] is not None


def test_confirm_already_confirmed():
    order = client.post("/orders", json=SAMPLE_ORDER).json()
    client.post(f"/orders/{order['id']}/confirm", json=TEST_PAYLOAD)
    response = client.post(f"/orders/{order['id']}/confirm", json=TEST_PAYLOAD)
    assert response.status_code == 400


def test_confirm_nonexistent_order():
    response = client.post("/orders/fake-id/confirm", json=TEST_PAYLOAD)
    assert response.status_code == 404


#DELETE /orders/{id} tests
def test_cancel_draft_order():
    order = client.post("/orders", json=SAMPLE_ORDER).json()
    response = client.delete(f"/orders/{order['id']}")
    assert response.status_code == 204


def test_cancelled_order_status():
    order = client.post("/orders", json=SAMPLE_ORDER).json()
    client.delete(f"/orders/{order['id']}")
    response = client.get(f"/orders/{order['id']}")
    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"


def test_cancel_confirmed_order_fails():
    order = client.post("/orders", json=SAMPLE_ORDER).json()
    client.post(f"/orders/{order['id']}/confirm", json=TEST_PAYLOAD)
    response = client.delete(f"/orders/{order['id']}")
    assert response.status_code == 400


def test_cancel_nonexistent_order():
    response = client.delete("/orders/fake-id")
    assert response.status_code == 404


def test_cannot_update_cancelled_order():
    order = client.post("/orders", json=SAMPLE_ORDER).json()
    client.delete(f"/orders/{order['id']}")
    new_items = [{"food_item": "Fries", "quantity": 1, "unit_price": 5.00}]
    response = client.put(f"/orders/{order['id']}", json={"items": new_items})
    assert response.status_code == 400


def test_cannot_confirm_cancelled_order():
    order = client.post("/orders", json=SAMPLE_ORDER).json()
    client.delete(f"/orders/{order['id']}")
    response = client.post(f"/orders/{order['id']}/confirm", json=TEST_PAYLOAD)
    assert response.status_code == 400
