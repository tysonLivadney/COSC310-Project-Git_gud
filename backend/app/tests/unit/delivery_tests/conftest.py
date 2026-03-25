import pytest
from unittest.mock import patch
from repositories.delivery_repo import save_all as save_deliveries, load_all as load_deliveries
from repositories.drivers_repo import save_all as save_drivers, load_all as load_drivers
from repositories.notifications_repo import save_all as save_notifications, load_all as load_notifications

VALID_DRIVER_PROFILE = {
    "user_id": "driver-1",
    "name": "John Smith",
    "phone": "+123456789",
    "vehicle_type": "Sedan",
    "license_plate": "ABC123",
    "available": True,
}


@pytest.fixture(autouse=True)
def save_and_restore():
    deliveries = load_deliveries()
    drivers = load_drivers()
    notifications = load_notifications()
    save_deliveries([])
    save_drivers([])
    save_notifications([])
    yield
    save_deliveries(deliveries)
    save_drivers(drivers)
    save_notifications(notifications)
