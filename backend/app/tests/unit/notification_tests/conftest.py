import pytest
from uuid import uuid4
from schemas.delivery import Delivery, DeliveryStatus
from schemas.notifications import NotificationType
from services import notifications_service
from repositories.notifications_repo import save_all as save_notifications, load_all as load_notifications


@pytest.fixture(autouse=True)
def save_and_restore():
    notifications = load_notifications()
    save_notifications([])
    yield
    save_notifications(notifications)


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