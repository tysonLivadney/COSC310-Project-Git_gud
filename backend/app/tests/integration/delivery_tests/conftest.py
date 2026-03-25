import pytest
from fastapi.testclient import TestClient
from main import app
from repositories.delivery_repo import save_all as save_deliveries, load_all as load_deliveries

client = TestClient(app)

VALID_DRIVER = {
    "id": "1",
    "name": "John Smith",
    "phone": "+123456789",
    "status": "online"
}


@pytest.fixture(autouse=True)
def save_and_restore():
    deliveries = load_deliveries()
    save_deliveries([])
    yield
    save_deliveries(deliveries)


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
    response = client.patch(f"/deliveries/{test_delivery['id']}/assign", json=VALID_DRIVER)
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