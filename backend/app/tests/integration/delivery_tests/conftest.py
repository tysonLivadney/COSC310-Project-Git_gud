import pytest
from fastapi.testclient import TestClient
from main import app
from services.auth_service import get_current_user
from schemas.auth import UserResponse
from repositories.delivery_repo import save_all as save_deliveries, load_all as load_deliveries
from repositories.drivers_repo import save_all as save_drivers, load_all as load_drivers
from repositories.users_repo import save_all as save_users, load_all as load_users
from repositories.sessions_repo import save_all as save_sessions, load_all as load_sessions

client = TestClient(app)

DRIVER_USER = {
    "name": "John Smith",
    "email": "driver@test.com",
    "password": "password123",
    "role": "driver",
}

VALID_PROFILE = {
    "phone": "+123456789",
    "vehicle_type": "Sedan",
    "license_plate": "ABC123",
}


@pytest.fixture(autouse=True)
def save_and_restore():
    deliveries = load_deliveries()
    drivers = load_drivers()
    users = load_users()
    sessions = load_sessions()
    save_deliveries([])
    save_drivers([])
    save_users([])
    save_sessions([])
    yield
    save_deliveries(deliveries)
    save_drivers(drivers)
    save_users(users)
    save_sessions(sessions)


def _register_driver():
    app.dependency_overrides.pop(get_current_user, None)
    client.post("/auth/register", json=DRIVER_USER)
    login = client.post("/auth/login", json={
        "email": DRIVER_USER["email"],
        "password": DRIVER_USER["password"],
    }).json()
    token = login["token"]
    driver_id = login["user"]["id"]
    client.post("/drivers/profile", json=VALID_PROFILE, headers={"Authorization": f"Bearer {token}"})
    app.dependency_overrides[get_current_user] = lambda: UserResponse(
        id=driver_id, name="John Smith", email="john@test.com", role="driver", created_at="2024-01-01T00:00:00Z"
    )
    return driver_id


@pytest.fixture
def test_delivery():
    response = client.post("/deliveries/", params={
        "order_id": "101",
        "pickup_address": "123 Pickup St",
        "dropoff_address": "456 Dropoff Ave"
    })
    assert response.status_code == 200
    return response.json()


@pytest.fixture
def test_assigned_delivery(test_delivery):
    driver_id = _register_driver()
    response = client.patch(f"/deliveries/{test_delivery['id']}/assign", params={"driver_id": driver_id})
    assert response.status_code == 200
    return response.json()


@pytest.fixture
def test_picked_up_delivery(test_assigned_delivery):
    response = client.patch(f"/deliveries/{test_assigned_delivery['id']}/pickup")
    assert response.status_code == 200
    return response.json()


@pytest.fixture
def test_in_transit_delivery(test_picked_up_delivery):
    response = client.patch(f"/deliveries/{test_picked_up_delivery['id']}/transit")
    assert response.status_code == 200
    return response.json()
