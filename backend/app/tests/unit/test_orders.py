from fastapi.testclient import TestClient
from repositories.orders_repo import load_all as load_orders, save_all as save_orders
import pytest
from main import app

client = TestClient(app)

SAMPLE_ORDER = {
    "restaurant_id": 1,
    "customer_id": "customer-1",
    "items": [{"food_item": "Burger", "quantity": 2, "unit_price": 10.00}],
}

SAMPLE_ORDER_2 = {
    "restaurant_id": 2,
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
    assert data["restaurant_id"] == 1
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
        "restaurant_id": 1,
        "customer_id": "customer-1",
        "items": [],
    })
    assert response.status_code == 422


def test_create_order_missing_fields():
    response = client.post("/orders", json={"restaurant_id": 1})
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
    client.post(f"/orders/{order['id']}/confirm")
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
