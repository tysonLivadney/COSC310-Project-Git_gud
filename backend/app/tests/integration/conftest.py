from fastapi.testclient import TestClient
import pytest
from main import app
from pathlib import Path
from uuid import uuid4

client = TestClient(app)

DATA_FILE_NOTIFICATIONS = Path("data/notifications.json")
DATA_FILE_DELIVERIES = Path("data/deliveries.json")

@pytest.fixture(autouse=True)
def clean_data_files():
    if DATA_FILE_NOTIFICATIONS.exists():
        DATA_FILE_NOTIFICATIONS.write_text("[]")
    if DATA_FILE_DELIVERIES.exists():
        DATA_FILE_DELIVERIES.write_text("[]")
    yield


@pytest.fixture
def test_delivery():
    return {
        "id": str(uuid4()),
        "order_id": "101",
        "pickup_address": "123 Pickup St",
        "dropoff_address": "456 Dropoff Ave",
        "status": "pending",
        "created_at": "2024-01-01T00:00:00",
        "updated_at": "2024-01-01T00:00:00"
    }

@pytest.fixture
def test_notification(test_delivery):
    response = client.post(
        "/notifications/",
        json=test_delivery,
        params={"notification_type": "delivery_created"}
    )
    assert response.status_code == 200
    return response.json()