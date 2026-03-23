from fastapi.testclient import TestClient
from repositories.orders_repo import load_all as load_orders, save_all as save_orders
from repositories.users_repo import load_all as load_users, save_all as save_users
from repositories.sessions_repo import load_all as load_sessions, save_all as save_sessions
import pytest
from main import app

client = TestClient(app)

MANAGER_USER = {
    "name": "Admin User",
    "email": "admin@test.com",
    "password": "password123",
    "role": "manager",
}

REGULAR_USER = {
    "name": "Regular User",
    "email": "regular@test.com",
    "password": "password123",
    "role": "user",
}

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


#save and restore content of storage files per test
@pytest.fixture(autouse=True)
def save_and_restore():
    orders = load_orders()
    users = load_users()
    sessions = load_sessions()
    save_orders([])
    save_users([])
    save_sessions([])
    yield
    save_orders(orders)
    save_users(users)
    save_sessions(sessions)


@pytest.fixture
def manager_token():
    client.post("/auth/register", json=MANAGER_USER)
    response = client.post("/auth/login", json={
        "email": MANAGER_USER["email"],
        "password": MANAGER_USER["password"],
    })
    return response.json()["token"]


@pytest.fixture
def user_token():
    client.post("/auth/register", json=REGULAR_USER)
    response = client.post("/auth/login", json={
        "email": REGULAR_USER["email"],
        "password": REGULAR_USER["password"],
    })
    return response.json()["token"]


def _auth_header(token):
    return {"Authorization": f"Bearer {token}"}


#GET /admin/orders tests
def test_get_all_orders_as_manager(manager_token):
    client.post("/orders", json=SAMPLE_ORDER)
    client.post("/orders", json=SAMPLE_ORDER_2)

    response = client.get("/admin/orders", headers=_auth_header(manager_token))
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_orders_empty(manager_token):
    response = client.get("/admin/orders", headers=_auth_header(manager_token))
    assert response.status_code == 200
    assert len(response.json()) == 0


def test_get_orders_unauthorized():
    response = client.get("/admin/orders")
    assert response.status_code == 401


def test_get_orders_as_regular_user(user_token):
    response = client.get("/admin/orders", headers=_auth_header(user_token))
    assert response.status_code == 403


def test_filter_orders_by_customer(manager_token):
    client.post("/orders", json=SAMPLE_ORDER)
    client.post("/orders", json=SAMPLE_ORDER_2)

    response = client.get(
        "/admin/orders", params={"customer_id": "customer-1"},
        headers=_auth_header(manager_token),
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["customer_id"] == "customer-1"


def test_filter_orders_by_restaurant(manager_token):
    client.post("/orders", json=SAMPLE_ORDER)
    client.post("/orders", json=SAMPLE_ORDER_2)

    response = client.get(
        "/admin/orders", params={"restaurant_id": 2},
        headers=_auth_header(manager_token),
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["restaurant_id"] == 2


def test_filter_orders_by_status(manager_token):
    order = client.post("/orders", json=SAMPLE_ORDER).json()
    client.post(f"/orders/{order['id']}/confirm")
    client.post("/orders", json=SAMPLE_ORDER_2)

    response = client.get(
        "/admin/orders", params={"status": "confirmed"},
        headers=_auth_header(manager_token),
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["status"] == "confirmed"


def test_filter_orders_no_match(manager_token):
    client.post("/orders", json=SAMPLE_ORDER)

    response = client.get(
        "/admin/orders", params={"customer_id": "nonexistent"},
        headers=_auth_header(manager_token),
    )
    assert response.status_code == 200
    assert len(response.json()) == 0


#GET /admin/reports tests
def test_reports_empty(manager_token):
    response = client.get("/admin/reports", headers=_auth_header(manager_token))
    assert response.status_code == 200
    data = response.json()
    assert data["total_revenue"] == 0.0
    assert data["revenue_per_restaurant"] == []


def test_reports_with_confirmed_orders(manager_token):
    order = client.post("/orders", json=SAMPLE_ORDER).json()
    client.post(f"/orders/{order['id']}/confirm")

    response = client.get("/admin/reports", headers=_auth_header(manager_token))
    assert response.status_code == 200
    data = response.json()
    assert data["total_revenue"] == 20.00  # 2 * 10.00
    assert len(data["revenue_per_restaurant"]) == 1
    assert data["revenue_per_restaurant"][0]["restaurant_id"] == 1
    assert data["revenue_per_restaurant"][0]["order_count"] == 1


def test_reports_ignores_draft_orders(manager_token):
    client.post("/orders", json=SAMPLE_ORDER)  # stays as draft

    response = client.get("/admin/reports", headers=_auth_header(manager_token))
    assert response.status_code == 200
    assert response.json()["total_revenue"] == 0.0


def test_reports_multiple_restaurants(manager_token):
    order1 = client.post("/orders", json=SAMPLE_ORDER).json()
    client.post(f"/orders/{order1['id']}/confirm")
    order2 = client.post("/orders", json=SAMPLE_ORDER_2).json()
    client.post(f"/orders/{order2['id']}/confirm")

    response = client.get("/admin/reports", headers=_auth_header(manager_token))
    assert response.status_code == 200
    data = response.json()
    assert data["total_revenue"] == 35.00  # 20.00 + 15.00
    assert len(data["revenue_per_restaurant"]) == 2


def test_reports_unauthorized():
    response = client.get("/admin/reports")
    assert response.status_code == 401


def test_reports_as_regular_user(user_token):
    response = client.get("/admin/reports", headers=_auth_header(user_token))
    assert response.status_code == 403
