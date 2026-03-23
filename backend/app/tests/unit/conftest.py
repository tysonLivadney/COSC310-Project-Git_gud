from uuid import uuid4
import pytest
from schemas.delivery import Delivery, DeliveryStatus
from schemas.notifications import NotificationType
from services import notifications_service
from pathlib import Path

DATA_FILE_NOTIFICATIONS = Path("data/notifications.json")

@pytest.fixture(autouse=True)
def clean_notifications_file():
    if DATA_FILE_NOTIFICATIONS.exists():
        DATA_FILE_NOTIFICATIONS.write_text("[]")
    yield
    if DATA_FILE_NOTIFICATIONS.exists():
        DATA_FILE_NOTIFICATIONS.write_text("[]")

@pytest.fixture
def sample_delivery():
    return Delivery(
        id=str(uuid4()),
        order_id="101",
        pickup_address="123 Pickup St",
        dropoff_address="456 Dropoff Ave",
        status=DeliveryStatus.PENDING
    )

@pytest.fixture
def sample_notification(sample_delivery):
    return notifications_service.notify(sample_delivery, NotificationType.DELIVERY_CREATED)