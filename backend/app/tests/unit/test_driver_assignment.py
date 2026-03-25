from fastapi.testclient import TestClient
from repositories.users_repo import load_all as load_users, save_all as save_users
from repositories.sessions_repo import load_all as load_sessions, save_all as save_sessions
from repositories.drivers_repo import load_all as load_drivers, save_all as save_drivers
from repositories.delivery_repo import load_all as load_deliveries, save_all as save_deliveries
import pytest
from main import app

client = TestClient(app)

DRIVER_USER = {
    "name": "Test Driver",
    "email": "driver@test.com",
    "password": "password123",
    "role": "driver",
}

VALID_PROFILE = {
    "phone": "+1234567890",
    "vehicle_type": "Sedan",
    "license_plate": "ABC123",
}


@pytest.fixture(autouse=True)
def save_and_restore():
    users = load_users()
    sessions = load_sessions()
    drivers = load_drivers()
    deliveries = load_deliveries()
    save_users([])
    save_sessions([])
    save_drivers([])
    save_deliveries([])
    yield
    save_users(users)
    save_sessions(sessions)
    save_drivers(drivers)
    save_deliveries(deliveries)


def _register_and_login(user_data):
    client.post("/auth/register", json=user_data)
    response = client.post("/auth/login", json={
        "email": user_data["email"],
        "password": user_data["password"],
    })
    return response.json()["token"]


def _auth_header(token):
    return {"Authorization": f"Bearer {token}"}


def _create_delivery():
    response = client.post("/deliveries/", params={
        "order_id": 101,
        "pickup_address": "123 Pickup St",
        "dropoff_address": "456 Dropoff Ave",
    })
    return response.json()


def _setup_driver():
    token = _register_and_login(DRIVER_USER)
    resp = client.post("/drivers/profile", json=VALID_PROFILE, headers=_auth_header(token))
    return resp.json()["user_id"]


def test_assign_registered_driver():
    delivery = _create_delivery()
    driver_id = _setup_driver()
    response = client.patch(f"/deliveries/{delivery['id']}/assign", params={"driver_id": driver_id})
    assert response.status_code == 200
    assert response.json()["status"] == "assigned"
    assert response.json()["driver"]["id"] == driver_id
    assert response.json()["driver"]["status"] == "busy"


def test_assign_nonexistent_driver():
    delivery = _create_delivery()
    response = client.patch(f"/deliveries/{delivery['id']}/assign", params={"driver_id": "fake-id"})
    assert response.status_code == 404


def test_assign_to_nonexistent_delivery():
    driver_id = _setup_driver()
    response = client.patch("/deliveries/fake-delivery/assign", params={"driver_id": driver_id})
    assert response.status_code == 404


def test_assign_driver_sets_driver_info():
    delivery = _create_delivery()
    driver_id = _setup_driver()
    response = client.patch(f"/deliveries/{delivery['id']}/assign", params={"driver_id": driver_id})
    driver = response.json()["driver"]
    assert driver["phone"] == "+1234567890"
    assert driver["status"] == "busy"


def test_cannot_assign_to_already_assigned():
    delivery = _create_delivery()
    driver_id = _setup_driver()
    client.patch(f"/deliveries/{delivery['id']}/assign", params={"driver_id": driver_id})
    response = client.patch(f"/deliveries/{delivery['id']}/assign", params={"driver_id": driver_id})
    assert response.status_code == 400
