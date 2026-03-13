from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

VALID_RESTAURANT = {
    "name": "Test Restaurant",
    "address": " 123 Address ", #testing that strip removes whitespace
    "description": "Example of a description.",
    "phone": "+123456789",
    "tags": ["tag1", "tag2"]
}

VALID_MENU = {
    "name": "Test Menu",
    "description": "Example of a description.",
}

#POST tests
def test_post_valid_menu(test_restaurant):
    response = client.post("/menus", json={**VALID_MENU,"restaurant_id": test_restaurant["id"]})
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == VALID_MENU["name"]
    assert "id" in data

def test_post_no_name(test_restaurant):
    response = client.post("/menus", json={**VALID_MENU,"name": "", "restaurant_id": test_restaurant["id"]})
    assert response.status_code == 422

def test_post_invalid_restaurant_id():
    response = client.post("/menus", json={**VALID_MENU,"restaurant_id": "00000"})
    assert response.status_code == 404

def test_post_missing_restaurant_id():
    response = client.post("/menus", json=VALID_MENU)
    assert response.status_code == 422

#GET tests

def test_get_menus():
    response = client.get("/menus")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_menus_empty_file():
    response = client.get("/menus")
    assert response.status_code == 200 #returns empty list
    assert len(response.json()) == 0

def test_get_menu_by_id(test_menu):
    response = client.get(f"/menus/{test_menu['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == test_menu["id"]

def test_get_menu_invalid_id():
    response = client.get("/menus/00000")
    assert response.status_code == 404

#PUT tests

def test_update_menu_name(test_menu):
    response = client.put(f"/menus/{test_menu['id']}", json={**VALID_MENU, "name": "Updated Menu Name"})
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Menu Name"

def test_update_menu_not_found():
    response = client.put("/menus/00000", json=VALID_MENU)
    assert response.status_code == 404

# DELETE tests

def test_delete_menu(test_menu):
    response = client.delete(f"/menus/{test_menu['id']}")
    assert response.status_code == 204
    assert client.get(f"/menus/{test_menu['id']}").status_code == 404

def test_delete_menu_not_found():
    response = client.delete("/menus/00000")
    assert response.status_code == 404

def test_delete_menu_cascade(test_menu):
    item = client.post("/menu-items", json={
        "name": "Test Item",
        "description": "Menu item description",
        "price": 10.00,
        "in_stock": True,
        "menu_id": test_menu["id"]
    }).json()
    client.delete(f"/menus/{test_menu['id']}")
    assert client.get(f"/menu-items/{item['id']}").status_code == 404