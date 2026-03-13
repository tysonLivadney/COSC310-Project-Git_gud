from fastapi.testclient import TestClient
import pytest
from main import app
from pathlib import Path

client = TestClient(app)

VALID_DELIVERY = {
    "id": 1,
    "order_id": 101,
    "pickup_address": "123 Pickup St",
    "dropoff_address": "456 Dropoff Ave",
    "status": "pending"
}


DATA_FILE = Path("data/notifications.json")

@pytest.fixture(autouse=True)
def clean_data_file():
    if DATA_FILE.exists():
        DATA_FILE.write_text("[]")
    yield
    if DATA_FILE.exists():
        DATA_FILE.write_text("[]")
        

@pytest.fixture
def test_notification():
    response = client.post(
    "/notifications/",
    json=VALID_DELIVERY,
    params={"notification_type" : "delivery_created"}     
    )
    assert response.status_code == 200
    return response.json()