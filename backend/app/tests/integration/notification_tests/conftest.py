import pytest
from fastapi.testclient import TestClient
from main import app
from repositories.notifications_repo import save_all as save_notifications, load_all as load_notifications
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
    notifications = load_notifications()
    save_deliveries([])
    save_notifications([])
    yield
    save_deliveries(deliveries)
    save_notifications(notifications)


@pytest.fixture
def test_delivery():
    response = client.post("/deliveries/", params={
        "order_id": "101",
        "pickup_address": "Pickup",
        "dropoff_address": "Dropoff"
    })
    assert response.status_code == 200
    return response.json()


@pytest.fixture
def test_notification(test_delivery):
    response = client.post(
        "/notifications/",
        json=test_delivery,
        params={"notification_type": "delivery_created"}
    )
    assert response.status_code == 200
    return response.json()