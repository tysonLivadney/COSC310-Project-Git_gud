import sys
import uuid
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))

from fastapi.testclient import TestClient
from main import app 
from repositories.reviews_repo import load_all as load_reviews, save_all as save_reviews 
from repositories.orders_repo import load_all as load_orders, save_all as save_orders  
from repositories.users_repo import load_all as load_users, save_all as save_users  
from repositories.sessions_repo import load_all as load_sessions, save_all as save_sessions  

client = TestClient(app)


def _unique_email():
    return f"test-{uuid.uuid4().hex[:8]}@example.com"


def _register_and_login(role="user"):
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
    data = login.json()
    return data["token"], data["user"]["id"]


def _auth_header(token):
    return {"Authorization": f"Bearer {token}"}


def _seed_completed_order(customer_id, restaurant_id=1):
    orders = load_orders()
    order_id = str(uuid.uuid4())
    orders.append({
        "id": order_id,
        "restaurant_id": restaurant_id,
        "customer_id": customer_id,
        "items": [{"food_item": "Burger", "quantity": 1, "unit_price": 9.99}],
        "status": "completed",
        "created_at": "2026-03-01T00:00:00Z",
    })
    save_orders(orders)
    return order_id


def _seed_draft_order(customer_id, restaurant_id=1):
    orders = load_orders()
    order_id = str(uuid.uuid4())
    orders.append({
        "id": order_id,
        "restaurant_id": restaurant_id,
        "customer_id": customer_id,
        "items": [{"food_item": "Pizza", "quantity": 1, "unit_price": 12.50}],
        "status": "draft",
        "created_at": "2026-03-01T00:00:00Z",
    })
    save_orders(orders)
    return order_id


def _cleanup():
    save_reviews([])
    save_orders([])


class TestCreateReview:

    def setup_method(self):
        _cleanup()

    def teardown_method(self):
        _cleanup()

    def test_create_review_with_rating_and_comment(self):
        token, user_id = _register_and_login("user")
        order_id = _seed_completed_order(user_id)
        resp = client.post("/reviews", json={
            "order_id": order_id,
            "rating": 5,
            "comment": "Excellent food!",
        }, headers=_auth_header(token))
        assert resp.status_code == 201
        data = resp.json()
        assert data["rating"] == 5
        assert data["comment"] == "Excellent food!"
        assert data["order_id"] == order_id
        assert data["user_id"] == user_id
        assert "id" in data
        assert "created_at" in data

    def test_create_review_without_comment(self):
        token, user_id = _register_and_login("user")
        order_id = _seed_completed_order(user_id)
        resp = client.post("/reviews", json={
            "order_id": order_id,
            "rating": 3,
        }, headers=_auth_header(token))
        assert resp.status_code == 201
        assert resp.json()["comment"] is None

    def test_create_review_stores_all_metadata(self):
        token, user_id = _register_and_login("user")
        order_id = _seed_completed_order(user_id, restaurant_id=42)
        resp = client.post("/reviews", json={
            "order_id": order_id,
            "rating": 4,
            "comment": "Good",
        }, headers=_auth_header(token))
        assert resp.status_code == 201
        data = resp.json()
        assert data["user_id"] == user_id
        assert data["order_id"] == order_id
        assert data["restaurant_id"] == 42
        assert data["rating"] == 4
        assert data["comment"] == "Good"
        assert data["created_at"] is not None

    def test_rating_below_1_rejected(self):
        token, user_id = _register_and_login("user")
        order_id = _seed_completed_order(user_id)
        resp = client.post("/reviews", json={
            "order_id": order_id,
            "rating": 0,
        }, headers=_auth_header(token))
        assert resp.status_code == 422

    def test_rating_above_5_rejected(self):
        token, user_id = _register_and_login("user")
        order_id = _seed_completed_order(user_id)
        resp = client.post("/reviews", json={
            "order_id": order_id,
            "rating": 6,
        }, headers=_auth_header(token))
        assert resp.status_code == 422

    def test_missing_rating_rejected(self):
        token, user_id = _register_and_login("user")
        order_id = _seed_completed_order(user_id)
        resp = client.post("/reviews", json={
            "order_id": order_id,
        }, headers=_auth_header(token))
        assert resp.status_code == 422

    def test_duplicate_review_rejected(self):
        token, user_id = _register_and_login("user")
        order_id = _seed_completed_order(user_id)
        client.post("/reviews", json={
            "order_id": order_id,
            "rating": 4,
        }, headers=_auth_header(token))
        resp = client.post("/reviews", json={
            "order_id": order_id,
            "rating": 5,
        }, headers=_auth_header(token))
        assert resp.status_code == 409

    def test_review_non_completed_order_rejected(self):
        token, user_id = _register_and_login("user")
        order_id = _seed_draft_order(user_id)
        resp = client.post("/reviews", json={
            "order_id": order_id,
            "rating": 3,
        }, headers=_auth_header(token))
        assert resp.status_code == 400

    def test_review_nonexistent_order_rejected(self):
        token, _ = _register_and_login("user")
        resp = client.post("/reviews", json={
            "order_id": "does-not-exist",
            "rating": 3,
        }, headers=_auth_header(token))
        assert resp.status_code == 404

    def test_review_other_users_order_rejected(self):
        _, user_a_id = _register_and_login("user")
        token_b, _ = _register_and_login("user")
        order_id = _seed_completed_order(user_a_id)
        resp = client.post("/reviews", json={
            "order_id": order_id,
            "rating": 4,
        }, headers=_auth_header(token_b))
        assert resp.status_code == 403


class TestUserEligibility:

    def setup_method(self):
        _cleanup()

    def teardown_method(self):
        _cleanup()

    def test_unauthenticated_user_rejected(self):
        resp = client.post("/reviews", json={
            "order_id": "some-order",
            "rating": 5,
        })
        assert resp.status_code == 401

    def test_owner_cannot_post_review(self):
        token, user_id = _register_and_login("owner")
        order_id = _seed_completed_order(user_id)
        resp = client.post("/reviews", json={
            "order_id": order_id,
            "rating": 5,
        }, headers=_auth_header(token))
        assert resp.status_code == 403

    def test_manager_cannot_post_review(self):
        token, user_id = _register_and_login("manager")
        order_id = _seed_completed_order(user_id)
        resp = client.post("/reviews", json={
            "order_id": order_id,
            "rating": 5,
        }, headers=_auth_header(token))
        assert resp.status_code == 403


class TestComments:

    def setup_method(self):
        _cleanup()

    def teardown_method(self):
        _cleanup()

    def test_comment_saved_with_rating(self):
        token, user_id = _register_and_login("user")
        order_id = _seed_completed_order(user_id)
        resp = client.post("/reviews", json={
            "order_id": order_id,
            "rating": 4,
            "comment": "Great service",
        }, headers=_auth_header(token))
        assert resp.status_code == 201
        assert resp.json()["comment"] == "Great service"

    def test_empty_comment_accepted(self):
        token, user_id = _register_and_login("user")
        order_id = _seed_completed_order(user_id)
        resp = client.post("/reviews", json={
            "order_id": order_id,
            "rating": 3,
            "comment": "",
        }, headers=_auth_header(token))
        assert resp.status_code == 201
        assert resp.json()["comment"] is None

    def test_whitespace_only_comment_normalized_to_null(self):
        token, user_id = _register_and_login("user")
        order_id = _seed_completed_order(user_id)
        resp = client.post("/reviews", json={
            "order_id": order_id,
            "rating": 2,
            "comment": "   ",
        }, headers=_auth_header(token))
        assert resp.status_code == 201
        assert resp.json()["comment"] is None

    def test_no_comment_field_accepted(self):
        token, user_id = _register_and_login("user")
        order_id = _seed_completed_order(user_id)
        resp = client.post("/reviews", json={
            "order_id": order_id,
            "rating": 5,
        }, headers=_auth_header(token))
        assert resp.status_code == 201
        assert resp.json()["comment"] is None


class TestViewingReviews:

    def setup_method(self):
        _cleanup()

    def teardown_method(self):
        _cleanup()

    def _create_review_directly(self, order_id, restaurant_id, user_id, rating, comment=None, created_at="2026-03-01T00:00:00Z"):
        reviews = load_reviews()
        reviews.append({
            "id": str(uuid.uuid4()),
            "order_id": order_id,
            "restaurant_id": restaurant_id,
            "user_id": user_id,
            "rating": rating,
            "comment": comment,
            "created_at": created_at,
        })
        save_reviews(reviews)

    def test_get_reviews_returns_list(self):
        resp = client.get("/reviews/restaurant/1")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_get_reviews_with_metadata(self):
        self._create_review_directly("o1", 1, "u1", 5, "Great", "2026-03-01T00:00:00Z")
        resp = client.get("/reviews/restaurant/1")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        review = data[0]
        assert review["rating"] == 5
        assert review["comment"] == "Great"
        assert review["created_at"] == "2026-03-01T00:00:00Z"

    def test_get_reviews_filters_by_restaurant(self):
        self._create_review_directly("o1", 1, "u1", 5)
        self._create_review_directly("o2", 2, "u2", 3)
        resp = client.get("/reviews/restaurant/1")
        assert len(resp.json()) == 1
        resp2 = client.get("/reviews/restaurant/2")
        assert len(resp2.json()) == 1

    def test_sort_most_recent_default(self):
        self._create_review_directly("o1", 1, "u1", 3, created_at="2026-03-01T00:00:00Z")
        self._create_review_directly("o2", 1, "u2", 5, created_at="2026-03-05T00:00:00Z")
        resp = client.get("/reviews/restaurant/1")
        data = resp.json()
        assert data[0]["created_at"] > data[1]["created_at"]

    def test_sort_highest(self):
        self._create_review_directly("o1", 1, "u1", 2)
        self._create_review_directly("o2", 1, "u2", 5)
        self._create_review_directly("o3", 1, "u3", 3)
        resp = client.get("/reviews/restaurant/1?sort=highest")
        ratings = [r["rating"] for r in resp.json()]
        assert ratings == [5, 3, 2]

    def test_sort_lowest(self):
        self._create_review_directly("o1", 1, "u1", 5)
        self._create_review_directly("o2", 1, "u2", 1)
        self._create_review_directly("o3", 1, "u3", 3)
        resp = client.get("/reviews/restaurant/1?sort=lowest")
        ratings = [r["rating"] for r in resp.json()]
        assert ratings == [1, 3, 5]

    def test_summary_average_and_count(self):
        self._create_review_directly("o1", 1, "u1", 4)
        self._create_review_directly("o2", 1, "u2", 2)
        resp = client.get("/reviews/restaurant/1/summary")
        assert resp.status_code == 200
        data = resp.json()
        assert data["average_rating"] == 3.0
        assert data["total_reviews"] == 2
        assert data["restaurant_id"] == 1

    def test_summary_no_reviews_returns_zero(self):
        resp = client.get("/reviews/restaurant/999/summary")
        assert resp.status_code == 200
        data = resp.json()
        assert data["average_rating"] == 0.0
        assert data["total_reviews"] == 0


class TestRestaurantRatingsView:

    def setup_method(self):
        _cleanup()

    def teardown_method(self):
        _cleanup()

    def _create_review_directly(self, order_id, restaurant_id, user_id, rating, comment=None, created_at="2026-03-01T00:00:00Z"):
        reviews = load_reviews()
        reviews.append({
            "id": str(uuid.uuid4()),
            "order_id": order_id,
            "restaurant_id": restaurant_id,
            "user_id": user_id,
            "rating": rating,
            "comment": comment,
            "created_at": created_at,
        })
        save_reviews(reviews)

    def test_view_returns_summary_and_reviews(self):
        self._create_review_directly("o1", 1, "u1", 4, "Nice")
        self._create_review_directly("o2", 1, "u2", 2, "Okay")
        resp = client.get("/reviews/restaurant/1/view")
        assert resp.status_code == 200
        data = resp.json()
        assert data["restaurant_id"] == 1
        assert data["average_rating"] == 3.0
        assert data["total_reviews"] == 2
        assert len(data["reviews"]) == 2

    def test_view_with_sort_highest(self):
        self._create_review_directly("o1", 1, "u1", 2)
        self._create_review_directly("o2", 1, "u2", 5)
        resp = client.get("/reviews/restaurant/1/view?sort=highest")
        data = resp.json()
        ratings = [r["rating"] for r in data["reviews"]]
        assert ratings == [5, 2]

    def test_view_empty_restaurant(self):
        resp = client.get("/reviews/restaurant/999/view")
        assert resp.status_code == 200
        data = resp.json()
        assert data["average_rating"] == 0.0
        assert data["total_reviews"] == 0
        assert data["reviews"] == []


class TestCustomerRoleEnforcement:

    def setup_method(self):
        _cleanup()

    def teardown_method(self):
        _cleanup()

    def test_user_role_can_create_review(self):
        token, user_id = _register_and_login("user")
        order_id = _seed_completed_order(user_id)
        resp = client.post("/reviews", json={
            "order_id": order_id,
            "rating": 5,
        }, headers=_auth_header(token))
        assert resp.status_code == 201

    def test_user_denied_duplicate_review(self):
        token, user_id = _register_and_login("user")
        order_id = _seed_completed_order(user_id)
        client.post("/reviews", json={
            "order_id": order_id,
            "rating": 4,
        }, headers=_auth_header(token))
        resp = client.post("/reviews", json={
            "order_id": order_id,
            "rating": 5,
        }, headers=_auth_header(token))
        assert resp.status_code == 409
