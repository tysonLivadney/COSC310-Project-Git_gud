from fastapi.testclient import TestClient
import pytest
from main import app
from pathlib import Path


VALID_DRIVER = {
    "id": 1,
    "name": "John Smith",
    "phone": "+123456789",
    "status": "online"
}


client = TestClient(app)

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
        "order_id": 101,
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

