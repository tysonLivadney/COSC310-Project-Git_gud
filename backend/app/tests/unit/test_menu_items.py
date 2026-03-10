from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

VALID_RESTAURANT = {
    "name": "Test Restaurant",
    "address": " 123 Address ",
    "description": "Example of a description.",
    "phone": "+123456789",
    "tags": ["tag1", "tag2"]
}

VALID_MENU = {
    "name": "Test Menu",
    "description": "Example of a description.",
}

VALID_MENU_ITEM = {
    "name": "Test Menu Item",
    "description": "Example of a description",
    "price": 10.00,
    "in_stock": True
}

#POST tests
def test_post_valid_menu_item(test_menu):
    response = client.post("/menu-items", json={**VALID_MENU_ITEM,"menu_id": test_menu["id"]})
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == VALID_MENU_ITEM["name"]
    assert "id" in data

def test_post_no_name(test_menu):
    response = client.post("/menu-items", json={**VALID_MENU_ITEM,"name": "", "menu_id": test_menu["id"]})
    assert response.status_code == 422

def test_post_invalid_restaurant_id():
    response = client.post("/menu-items", json={**VALID_MENU_ITEM,"menu_id": "00000"})
    assert response.status_code == 404

def test_post_missing_restaurant_id():
    response = client.post("/menu-items", json=VALID_MENU_ITEM)
    assert response.status_code == 422

#GET tests

def test_get_menu_items():
    response = client.get("/menu-items")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_menu_items_empty_file():
    response = client.get("/menu-items")
    assert response.status_code == 200
    assert len(response.json()) == 0

def test_get_menu_item_by_id(test_menu_item):
    response = client.get(f"/menu-items/{test_menu_item['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == test_menu_item["id"]

def test_get_menu_invalid_id():
    response = client.get("/menu-items/00000")
    assert response.status_code == 404

#PUT tests

def test_update_menu_name(test_menu_item):
    response = client.put(f"/menu-items/{test_menu_item['id']}", json={**VALID_MENU_ITEM, "name": "Updated Menu Item Name"})
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Menu Item Name"

def test_update_menu_not_found():
    response = client.put("/menu-items/00000", json=VALID_MENU_ITEM)
    assert response.status_code == 404

# DELETE tests

def test_delete_menu(test_menu_item):
    response = client.delete(f"/menu-items/{test_menu_item['id']}")
    assert response.status_code == 204
    assert client.get(f"/menu-items/{test_menu_item['id']}").status_code == 404

def test_delete_menu_not_found():
    response = client.delete("/menu-items/00000")
    assert response.status_code == 404
