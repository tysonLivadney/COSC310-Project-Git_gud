from fastapi.testclient import TestClient
import pytest
from main import app
from pathlib import Path
from repositories.restaurants_repo import save_all as save_restaurants, load_all as load_restaurants
from repositories.menus_repo import save_all as save_menus, load_all as load_menus
from repositories.menu_items_repo import save_all as save_menu_items, load_all as load_menu_items
from schemas.delivery import Delivery
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

OWNER_USER = {
    "name": "Test Owner",
    "email": "owner@test.com",
    "password": "password123",
    "role": "owner"
}

def register_and_login(user_data):
    client.post("/auth/register", json=user_data)
    response = client.post("/auth/login", json={
        "email": user_data["email"],
        "password": user_data["password"],
    })
    return response.json()["token"]

def _auth_header(token):
    return {"Authorization": f"Bearer {token}"}

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
    return client.post("/restaurants", json=VALID_RESTAURANT, headers=_auth_header(register_and_login(OWNER_USER))).json()

@pytest.fixture
def test_menu(test_restaurant):
    return client.post("/menus", json={**VALID_MENU, "restaurant_id": test_restaurant["id"]}).json()

@pytest.fixture
def test_menu_item(test_menu):
    return client.post("/menu-items", json={**VALID_MENU_ITEM, "menu_id": test_menu["id"]}).json()

