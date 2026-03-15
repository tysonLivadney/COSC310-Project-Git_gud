from repositories.restaurants_repo import save_all as save_restaurants, load_all as load_restaurants
from repositories.menus_repo import save_all as save_menus, load_all as load_menus
from repositories.menu_items_repo import save_all as save_menu_items, load_all as load_menu_items
from fastapi.testclient import TestClient
from fastapi import FastAPI, status
import pytest
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

@pytest.fixture(autouse=True)
def save_and_restore():
    restaurants = load_restaurants()
    menus = load_menus()
    menu_items = load_menu_items()
    save_menu_items([])
    save_menus([])
    save_restaurants([])
    yield
    save_restaurants(restaurants)
    save_menus(menus)
    save_menu_items(menu_items)

@pytest.fixture
def test_restaurant():
    return client.post("/restaurants", json=VALID_RESTAURANT).json()

@pytest.fixture
def test_menu(test_restaurant):
    return client.post("/menus", json={**VALID_MENU,"restaurant_id": test_restaurant["id"]}).json()

@pytest.fixture
def test_menu_item(test_menu):
    return client.post("/menu-items", json={**VALID_MENU_ITEM,"menu_id": test_menu["id"]}).json()from fastapi.testclient import TestClient
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

