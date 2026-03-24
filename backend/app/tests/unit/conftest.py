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
    assert response.status_code == 200
    return response.json()
from repositories.restaurants_repo import save_all as save_restaurants, load_all as load_restaurants
from repositories.menus_repo import save_all as save_menus, load_all as load_menus
from repositories.menu_items_repo import save_all as save_menu_items, load_all as load_menu_items
from repositories.payments_repo import save_all as save_payments, load_all as load_payments
from fastapi.testclient import TestClient
from fastapi import FastAPI, status
import pytest
from pathlib import Path
from main import app

client = TestClient(app)

VALID_RESTAURANT = {
    "name": "Test Restaurant",
    "address": " 123 Address ",
    "description": "Example of a description.",
    "phone": "+123456789",
    "rating": 5,
    "tags": ["tag1", "tag2"],
    "estimated_delivery_time": 10
}

VALID_MENU = {
    "name": "Test Menu",
    "description": "Test menu description that is long enough.",
}

VALID_MENU_ITEM = {
    "name": "Test Menu Item",
    "description": "Example of a description",
    "price": 10.00,
    "in_stock": True
}

VALID_DRIVER = {
    "id": 1,
    "name": "John Smith",
    "phone": "+123456789",
    "status": "online"
}

@pytest.fixture(autouse=True)
def save_and_restore():
    restaurants = load_restaurants()
    menus = load_menus()
    menu_items = load_menu_items()
    payments = load_payments()
    save_menu_items([])
    save_menus([])
    save_restaurants([])
    save_payments([])
    yield
    save_restaurants(restaurants)
    save_menus(menus)
    save_menu_items(menu_items)
    save_payments(payments)

@pytest.fixture
def test_restaurant():
    return client.post("/restaurants", json=VALID_RESTAURANT).json()

@pytest.fixture
def sample_notification(sample_delivery):
    return notifications_service.notify(sample_delivery, NotificationType.DELIVERY_CREATED)