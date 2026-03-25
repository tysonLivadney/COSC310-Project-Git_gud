import uuid

import pytest
from fastapi.testclient import TestClient

from main import app
from repositories.orders_repo import load_all as load_orders, save_all as save_orders
from repositories.reviews_repo import load_all as load_reviews, save_all as save_reviews
from repositories.sessions_repo import load_all as load_sessions, save_all as save_sessions
from repositories.users_repo import load_all as load_users, save_all as save_users


client = TestClient(app)


def _register_and_login_user() -> tuple[str, str]:
    email = f"review-user-{uuid.uuid4().hex[:8]}@example.com"
    password = "testpass123"

    register_response = client.post(
        "/auth/register",
        json={
            "name": "Review User",
            "email": email,
            "password": password,
            "role": "user",
        },
    )
    assert register_response.status_code == 201

    login_response = client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )
    assert login_response.status_code == 200

    login_payload = login_response.json()
    return login_payload["token"], login_payload["user"]["id"]


def _seed_order(customer_id: str, status: str) -> str:
    orders = load_orders()
    order_id = str(uuid.uuid4())
    orders.append(
        {
            "id": order_id,
            "restaurant_id": 1,
            "customer_id": customer_id,
            "items": [{"food_item": "Burger", "quantity": 1, "unit_price": 9.99}],
            "status": status,
            "created_at": "2026-03-01T00:00:00Z",
        }
    )
    save_orders(orders)
    return order_id


@pytest.fixture(autouse=True)
def isolate_review_eligibility_data():
    original_orders = load_orders()
    original_reviews = load_reviews()
    original_users = load_users()
    original_sessions = load_sessions()

    save_orders([])
    save_reviews([])
    save_users([])
    save_sessions([])

    yield

    save_orders(original_orders)
    save_reviews(original_reviews)
    save_users(original_users)
    save_sessions(original_sessions)


def test_create_review_requires_login():
    response = client.post(
        "/reviews",
        json={"order_id": "missing-auth-order", "rating": 5},
    )
    assert response.status_code == 401


def test_create_review_rejects_non_completed_order():
    token, user_id = _register_and_login_user()
    order_id = _seed_order(user_id, status="draft")

    response = client.post(
        "/reviews",
        json={"order_id": order_id, "rating": 4},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 400


def test_create_review_rejects_duplicate_for_same_order():
    token, user_id = _register_and_login_user()
    order_id = _seed_order(user_id, status="completed")

    first_response = client.post(
        "/reviews",
        json={"order_id": order_id, "rating": 4},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert first_response.status_code == 201

    second_response = client.post(
        "/reviews",
        json={"order_id": order_id, "rating": 5},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert second_response.status_code == 409
