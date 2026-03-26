from repositories.restaurants_repo import save_all as save_restaurants, load_all as load_restaurants
from repositories.menus_repo import save_all as save_menus, load_all as load_menus
from repositories.menu_items_repo import save_all as save_menu_items, load_all as load_menu_items
from repositories.drivers_repo import save_all as save_drivers, load_all as load_drivers
from repositories.users_repo import save_all as save_users, load_all as load_users
from repositories.sessions_repo import save_all as save_sessions, load_all as load_sessions
from fastapi.testclient import TestClient
import pytest
from pathlib import Path

from main import app
from services.auth_dependencies import get_current_user
from schemas.auth import UserResponse


def _mock_driver():
    return UserResponse(id="1", name="John Smith", email="john@test.com", role="driver", created_at="2024-01-01T00:00:00Z")

client = TestClient(app)

@pytest.fixture(autouse=True)
def mock_driver_auth():
    app.dependency_overrides[get_current_user] = _mock_driver
    yield
    app.dependency_overrides.pop(get_current_user, None)

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


VALID_DELIVERY = {
    "id": "1",
    "order_id": "101",
    "pickup_address": "123 Pickup St",
    "dropoff_address": "456 Dropoff Ave",
    "status": "pending"
}

@pytest.fixture(autouse=True)
def save_and_restore():
    restaurants = load_restaurants()
    menus = load_menus()
    menu_items = load_menu_items()
    drivers = load_drivers()
    users = load_users()
    sessions = load_sessions()
    save_menu_items([])
    save_menus([])
    save_restaurants([])
    save_drivers([])
    save_users([])
    save_sessions([])
    yield
    save_restaurants(restaurants)
    save_menus(menus)
    save_menu_items(menu_items)
    save_drivers(drivers)
    save_users(users)
    save_sessions(sessions)

DATA_FILE_DELIVERIES = Path("data/deliveries.json")

@pytest.fixture(autouse=True)
def clean_delivery_file():
    if DATA_FILE_DELIVERIES.exists():
        DATA_FILE_DELIVERIES.write_text("[]")
    yield
    if DATA_FILE_DELIVERIES.exists():
        DATA_FILE_DELIVERIES.write_text("[]")

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
def registered_driver():
    app.dependency_overrides.pop(get_current_user, None)
    client.post("/auth/register", json=DRIVER_USER)
    login = client.post("/auth/login", json={
        "email": DRIVER_USER["email"],
        "password": DRIVER_USER["password"],
    }).json()
    token = login["token"]
    driver_id = login["user"]["id"]
    client.post("/drivers/profile", json=VALID_PROFILE, headers={"Authorization": f"Bearer {token}"})
    app.dependency_overrides[get_current_user] = lambda: UserResponse(id=driver_id, name="John Smith", email="john@test.com", role="driver", created_at="2024-01-01T00:00:00Z")
    return driver_id

@pytest.fixture
def test_assigned_delivery(test_delivery, registered_driver):
    response = client.patch(f"/deliveries/{test_delivery['id']}/assign", params={"driver_id": registered_driver})
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

@pytest.fixture
def test_notification():
    response = client.post(
        "/notifications/",
        json=VALID_DELIVERY,
        params={"notification_type": "delivery_created"}
    )
    assert response.status_code == 200
    return response.json()
