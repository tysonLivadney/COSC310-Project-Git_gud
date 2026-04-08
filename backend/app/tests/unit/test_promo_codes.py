from fastapi.testclient import TestClient
from repositories.promo_codes_repo import load_all as load_promos, save_all as save_promos
from repositories.users_repo import load_all as load_users, save_all as save_users
from repositories.sessions_repo import load_all as load_sessions, save_all as save_sessions
import pytest
from main import app

client = TestClient(app)

MANAGER_USER = {
    "name": "Promo Admin",
    "email": "promoadmin@test.com",
    "password": "password123",
    "role": "manager",
}


@pytest.fixture(autouse=True)
def save_and_restore():
    promos = load_promos()
    users = load_users()
    sessions = load_sessions()
    save_promos([])
    save_users([])
    save_sessions([])
    yield
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


def test_create_promo_code():
    token = get_manager_token()
    resp = client.post("/promo-codes", json={
        "code": "SAVE20",
        "discount_type": "percentage",
        "discount_value": 20,
    }, headers={"Authorization": f"Bearer {token}"})

    assert resp.status_code == 201
    data = resp.json()
    assert data["code"] == "SAVE20"
    assert data["discount_type"] == "percentage"
    assert data["discount_value"] == 20
    assert data["active"] is True
    assert data["usage_count"] == 0


def test_create_duplicate_code():
    token = get_manager_token()
    client.post("/promo-codes", json={
        "code": "DUP10",
        "discount_type": "flat",
        "discount_value": 10,
    }, headers={"Authorization": f"Bearer {token}"})

    resp = client.post("/promo-codes", json={
        "code": "dup10",
        "discount_type": "flat",
        "discount_value": 5,
    }, headers={"Authorization": f"Bearer {token}"})

    assert resp.status_code == 409


def test_list_promo_codes():
    token = get_manager_token()
    client.post("/promo-codes", json={
        "code": "CODE1",
        "discount_type": "flat",
        "discount_value": 5,
    }, headers={"Authorization": f"Bearer {token}"})
    client.post("/promo-codes", json={
        "code": "CODE2",
        "discount_type": "percentage",
        "discount_value": 15,
    }, headers={"Authorization": f"Bearer {token}"})

    resp = client.get("/promo-codes", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_validate_valid_code():
    token = get_manager_token()
    client.post("/promo-codes", json={
        "code": "VALID10",
        "discount_type": "flat",
        "discount_value": 10,
    }, headers={"Authorization": f"Bearer {token}"})

    resp = client.post("/promo-codes/validate", json={
        "code": "VALID10",
        "order_subtotal": 50.00,
    })
    assert resp.status_code == 200
    assert resp.json()["valid"] is True


def test_validate_expired_code():
    token = get_manager_token()
    client.post("/promo-codes", json={
        "code": "EXPIRED",
        "discount_type": "flat",
        "discount_value": 10,
        "expiry_date": "2020-01-01T00:00:00",
    }, headers={"Authorization": f"Bearer {token}"})

    resp = client.post("/promo-codes/validate", json={
        "code": "EXPIRED",
        "order_subtotal": 50.00,
    })
    assert resp.status_code == 400
    assert "expired" in resp.json()["detail"].lower()


def test_validate_maxed_out_code():
    token = get_manager_token()
    client.post("/promo-codes", json={
        "code": "MAXED",
        "discount_type": "flat",
        "discount_value": 5,
        "max_uses": 0,
    }, headers={"Authorization": f"Bearer {token}"})

    # manually set usage_count to match max
    promos = load_promos()
    for p in promos:
        if p["code"] == "MAXED":
            p["max_uses"] = 1
            p["usage_count"] = 1
    save_promos(promos)

    resp = client.post("/promo-codes/validate", json={
        "code": "MAXED",
        "order_subtotal": 50.00,
    })
    assert resp.status_code == 400
    assert "usage limit" in resp.json()["detail"].lower()


def test_validate_below_min_order():
    token = get_manager_token()
    client.post("/promo-codes", json={
        "code": "MIN50",
        "discount_type": "percentage",
        "discount_value": 10,
        "min_order_amount": 50.00,
    }, headers={"Authorization": f"Bearer {token}"})

    resp = client.post("/promo-codes/validate", json={
        "code": "MIN50",
        "order_subtotal": 30.00,
    })
    assert resp.status_code == 400
    assert "at least" in resp.json()["detail"].lower()


def test_validate_inactive_code():
    token = get_manager_token()
    client.post("/promo-codes", json={
        "code": "INACTIVE",
        "discount_type": "flat",
        "discount_value": 10,
    }, headers={"Authorization": f"Bearer {token}"})

    # deactivate it
    client.delete("/promo-codes/INACTIVE", headers={"Authorization": f"Bearer {token}"})

    resp = client.post("/promo-codes/validate", json={
        "code": "INACTIVE",
        "order_subtotal": 50.00,
    })
    assert resp.status_code == 400
    assert "no longer active" in resp.json()["detail"].lower()


def test_validate_nonexistent_code():
    resp = client.post("/promo-codes/validate", json={
        "code": "DOESNTEXIST",
        "order_subtotal": 50.00,
    })
    assert resp.status_code == 404


def test_deactivate_code():
    token = get_manager_token()
    client.post("/promo-codes", json={
        "code": "KILLME",
        "discount_type": "flat",
        "discount_value": 10,
    }, headers={"Authorization": f"Bearer {token}"})

    resp = client.delete("/promo-codes/KILLME", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["active"] is False


def test_requires_manager_to_create():
    resp = client.post("/promo-codes", json={
        "code": "NOAUTH",
        "discount_type": "flat",
        "discount_value": 10,
    })
    assert resp.status_code == 401
