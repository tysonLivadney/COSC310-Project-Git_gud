import uuid
from fastapi.testclient import TestClient
from app.main import app
client = TestClient(app)

def _unique_email():
    return f"test-{uuid.uuid4().hex[:8]}@example.com"

def _register_and_login(role="owner"):
    email = _unique_email()
    password = "testpass123"

    reg = client.post("/auth/register", json={
        "name": "Test User",
        "email": email,
        "password": password,
        "role": role,
    })
    assert reg.status_code == 201

    login = client.post("/auth/login", json={
        "email": email,
        "password": password,
    })
    assert login.status_code == 200
    return login.json()["token"]


def _auth_header(token):
    return {"Authorization": f"Bearer {token}"}


def test_health_check():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_get_items():
    resp = client.get("/items")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_create_item():
    token = _register_and_login(role="owner")
    resp = client.post(
        "/items",
        json={"title": "Test Item", "category": "food", "tags": ["pytest"]},
        headers=_auth_header(token),
    )
    assert resp.status_code in (200, 201)
    data = resp.json()
    assert data["title"] == "Test Item"
    assert "id" in data


def test_get_item_by_id():
    token = _register_and_login(role="owner")

    create_resp = client.post(
        "/items",
        json={"title": "Lookup Item", "category": "drink", "tags": []},
        headers=_auth_header(token),
    )
    assert create_resp.status_code in (200, 201)
    item_id = create_resp.json()["id"]

    resp = client.get(f"/items/{item_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == item_id
    assert resp.json()["title"] == "Lookup Item"


def test_delete_item():
    token = _register_and_login(role="owner")

    create_resp = client.post(
        "/items",
        json={"title": "Delete Me", "category": "misc", "tags": []},
        headers=_auth_header(token),
    )
    assert create_resp.status_code in (200, 201)
    item_id = create_resp.json()["id"]

    del_resp = client.delete(f"/items/{item_id}", headers=_auth_header(token))
    assert del_resp.status_code == 204

    get_resp = client.get(f"/items/{item_id}")
    assert get_resp.status_code == 404


def test_auth_register():
    email = _unique_email()
    resp = client.post("/auth/register", json={
        "name": "New User",
        "email": email,
        "password": "securepass",
        "role": "user",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == email.lower()
    assert data["role"] == "user"
    assert "id" in data


def test_auth_login():
    email = _unique_email()
    password = "logintest123"

    client.post("/auth/register", json={
        "name": "Login User",
        "email": email,
        "password": password,
        "role": "user",
    })

    resp = client.post("/auth/login", json={
        "email": email,
        "password": password,
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "token" in data
    assert data["token_type"] == "bearer"
    assert "expires_at" in data


def test_get_orders():
    resp = client.get("/orders")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_create_order():
    resp = client.post("/orders", json={
        "restaurant_id": 1,
        "customer_id": "cust-001",
        "items": [
            {"food_item": "Burger", "quantity": 2, "unit_price": 9.99},
        ],
    })
    assert resp.status_code in (200, 201)
    data = resp.json()
    assert data["status"] == "draft"
    assert "id" in data


def test_confirm_order():
    create_resp = client.post("/orders", json={
        "restaurant_id": 1,
        "customer_id": "cust-002",
        "items": [
            {"food_item": "Pizza", "quantity": 1, "unit_price": 12.50},
        ],
    })
    assert create_resp.status_code in (200, 201)
    order_id = create_resp.json()["id"]

    resp = client.post(f"/orders/{order_id}/confirm")
    assert resp.status_code == 200
    assert resp.json()["status"] == "confirmed"
