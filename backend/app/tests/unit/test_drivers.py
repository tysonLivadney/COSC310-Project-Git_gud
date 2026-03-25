from fastapi.testclient import TestClient
from repositories.users_repo import load_all as load_users, save_all as save_users
from repositories.sessions_repo import load_all as load_sessions, save_all as save_sessions
from repositories.drivers_repo import load_all as load_drivers, save_all as save_drivers
import pytest
from main import app

client = TestClient(app)

DRIVER_USER = {
    "name": "Test Driver",
    "email": "driver@test.com",
    "password": "password123",
    "role": "driver",
}

REGULAR_USER = {
    "name": "Regular User",
    "email": "regular@test.com",
    "password": "password123",
    "role": "user",
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
    save_users([])
    save_sessions([])
    save_drivers([])
    yield
    save_users(users)
    save_sessions(sessions)
    save_drivers(drivers)


def _register_and_login(user_data):
    client.post("/auth/register", json=user_data)
    response = client.post("/auth/login", json={
        "email": user_data["email"],
        "password": user_data["password"],
    })
    return response.json()["token"]


def _auth_header(token):
    return {"Authorization": f"Bearer {token}"}


#POST /drivers/profile tests
def test_create_driver_profile():
    token = _register_and_login(DRIVER_USER)
    response = client.post("/drivers/profile", json=VALID_PROFILE, headers=_auth_header(token))
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Driver"
    assert data["phone"] == "+1234567890"
    assert data["vehicle_type"] == "Sedan"
    assert data["license_plate"] == "ABC123"
    assert data["available"] == False


def test_create_profile_duplicate():
    token = _register_and_login(DRIVER_USER)
    client.post("/drivers/profile", json=VALID_PROFILE, headers=_auth_header(token))
    response = client.post("/drivers/profile", json=VALID_PROFILE, headers=_auth_header(token))
    assert response.status_code == 409


def test_create_profile_as_regular_user():
    token = _register_and_login(REGULAR_USER)
    response = client.post("/drivers/profile", json=VALID_PROFILE, headers=_auth_header(token))
    assert response.status_code == 403


def test_create_profile_unauthorized():
    response = client.post("/drivers/profile", json=VALID_PROFILE)
    assert response.status_code == 401


#GET /drivers/profile tests
def test_get_driver_profile():
    token = _register_and_login(DRIVER_USER)
    client.post("/drivers/profile", json=VALID_PROFILE, headers=_auth_header(token))
    response = client.get("/drivers/profile", headers=_auth_header(token))
    assert response.status_code == 200
    assert response.json()["phone"] == "+1234567890"


def test_get_profile_not_created():
    token = _register_and_login(DRIVER_USER)
    response = client.get("/drivers/profile", headers=_auth_header(token))
    assert response.status_code == 404


#PUT /drivers/profile tests
def test_update_driver_profile():
    token = _register_and_login(DRIVER_USER)
    client.post("/drivers/profile", json=VALID_PROFILE, headers=_auth_header(token))
    response = client.put("/drivers/profile", json={"phone": "+9999999999"}, headers=_auth_header(token))
    assert response.status_code == 200
    assert response.json()["phone"] == "+9999999999"
    assert response.json()["vehicle_type"] == "Sedan"


def test_update_availability():
    token = _register_and_login(DRIVER_USER)
    client.post("/drivers/profile", json=VALID_PROFILE, headers=_auth_header(token))
    response = client.put("/drivers/profile", json={"available": True}, headers=_auth_header(token))
    assert response.status_code == 200
    assert response.json()["available"] == True


#GET /drivers/available tests
def test_list_available_drivers_empty():
    token = _register_and_login({"name": "Manager", "email": "manager@test.com", "password": "password123", "role": "manager"})
    response = client.get("/drivers/available", headers=_auth_header(token))
    assert response.status_code == 200
    assert response.json() == []


def test_list_available_drivers():
    driver_token = _register_and_login(DRIVER_USER)
    client.post("/drivers/profile", json=VALID_PROFILE, headers=_auth_header(driver_token))
    client.put("/drivers/profile", json={"available": True}, headers=_auth_header(driver_token))

    manager_token = _register_and_login({"name": "Manager", "email": "manager@test.com", "password": "password123", "role": "manager"})
    response = client.get("/drivers/available", headers=_auth_header(manager_token))
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "Test Driver"


def test_list_available_as_regular_user():
    token = _register_and_login(REGULAR_USER)
    response = client.get("/drivers/available", headers=_auth_header(token))
    assert response.status_code == 403
