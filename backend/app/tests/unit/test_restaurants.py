from services.restaurants_service import *
from repositories.restaurants_repo import save_all as save_restaurants, load_all as load_restaurants
from repositories.menus_repo import save_all as save_menus, load_all as load_menus
from repositories.menu_items_repo import save_all as save_menu_items, load_all as load_menu_items
import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient
from main import app
from pathlib import Path

client = TestClient(app)

VALID_RESTAURANT = {
    "name": "Test Restaurant",
    "address": " 123 Address ", #testing that strip removes whitespace
    "description": "Example of a description.",
    "phone": "+123456789",
    "tags": ["tag1", "tag2"]
}

#save and restore content of storage files per test
@pytest.fixture(autouse=True)
def save_and_restore():
    restaurants = load_restaurants()
    menus = load_menus()
    menu_items = load_menu_items()
    #wipe restaurants.json
    save_menu_items([])
    save_menus([])
    save_restaurants([])
    yield
    save_restaurants(restaurants)
    save_menus(menus)
    save_menu_items(menu_items)

#POST tests
def test_post_valid_restaurant():
    response = client.post("/restaurants", json=VALID_RESTAURANT)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == VALID_RESTAURANT["name"]
    assert data["address"] == "123 Address"
    assert "id" in data

def test_post_no_name():
    invalid_restaurant = {**VALID_RESTAURANT, "name": ""}
    response = client.post("/restaurants", json=invalid_restaurant)
    assert response.status_code == 422

def test_post_invalid_phone():
    invalid_restaurant = {**VALID_RESTAURANT, "phone": "a123456789"} #characters not allowed
    response = client.post("/restaurants", json=invalid_restaurant)
    assert response.status_code == 422

def test_desc_too_short():
    invalid_restaurant = {**VALID_RESTAURANT, "description": "Too short"}
    response = client.post("/restaurants", json=invalid_restaurant)
    assert response.status_code == 422

def test_too_many_tags():
    invalid_restaurant = {**VALID_RESTAURANT, "tags": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11"]}
    response = client.post("/restaurants", json=invalid_restaurant)
    assert response.status_code == 422

#GET tests
def test_get_restaurants(): 
    client.post("/restaurants", json=VALID_RESTAURANT)
    client.post("/restaurants", json=VALID_RESTAURANT)

    response = client.get("/restaurants")
    assert response.status_code == 200
    assert len(response.json()) == 2

def test_get_restaurants_empty_file():
    response = client.get("/restaurants")
    assert len(response.json()) == 0 #returns empty list if no restaurants

def test_get_restaurant_by_id():
    testaurant = client.post("/restaurants", json=VALID_RESTAURANT).json()

    response = client.get(f"/restaurants/{testaurant['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == testaurant["id"]

def test_get_restaurant_invalid_id():
    response = client.get("/restaurants/00000")
    assert response.status_code == 404
    

