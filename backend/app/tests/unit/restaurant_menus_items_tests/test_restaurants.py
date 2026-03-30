from fastapi.testclient import TestClient
from main import app
from services.auth_dependencies import get_current_user
from schemas.auth import UserResponse

client = TestClient(app)

VALID_RESTAURANT = {
    "name": "Test Restaurant",
    "address": " 123 Address ",
    "description": "Example of a description.",
    "phone": "+123456789",
    "rating": 5,
    "tags": ["italian", "pizza"]
}

VALID_MENU = {
    "name": "Test Menu",
    "description": "Test menu description that is long enough.",
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

def test_post_valid_restaurant():
    token = register_and_login(OWNER_USER)
    response = client.post("/restaurants", json=VALID_RESTAURANT, headers=_auth_header(token))
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == VALID_RESTAURANT["name"]
    assert data["address"] == "123 Address"
    assert "id" in data

def test_post_no_name():
    invalid_restaurant = {**VALID_RESTAURANT, "name": ""}
    token = register_and_login(OWNER_USER)
    response = client.post("/restaurants", json=invalid_restaurant, headers=_auth_header(token))
    assert response.status_code == 422

def test_name_too_long():
    invalid_restaurant = {**VALID_RESTAURANT, "name": "123456789012345678901234567890123456789012345678901"}
    token = register_and_login(OWNER_USER)
    response = client.post("/restaurants", json=invalid_restaurant, headers=_auth_header(token))
    assert response.status_code == 422

def test_post_invalid_phone():
    invalid_restaurant = {**VALID_RESTAURANT, "phone": "a123456789"}
    token = register_and_login(OWNER_USER)
    response = client.post("/restaurants", json=invalid_restaurant, headers=_auth_header(token))
    assert response.status_code == 422

def test_desc_too_short():
    invalid_restaurant = {**VALID_RESTAURANT, "description": "Too short"}
    token = register_and_login(OWNER_USER)
    response = client.post("/restaurants", json=invalid_restaurant, headers=_auth_header(token))
    assert response.status_code == 422

def test_too_many_tags():
    invalid_restaurant = {**VALID_RESTAURANT, "tags": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11"]}
    token = register_and_login(OWNER_USER)
    response = client.post("/restaurants", json=invalid_restaurant, headers=_auth_header(token))
    assert response.status_code == 422

def test_get_restaurants(): 
    token = register_and_login(OWNER_USER)

    client.post("/restaurants", json=VALID_RESTAURANT, headers=_auth_header(token))
    client.post("/restaurants", json=VALID_RESTAURANT, headers=_auth_header(token))

    response = client.get("/restaurants")
    assert response.status_code == 200
    assert len(response.json()) == 2

def test_get_restaurants_empty_file():
    token = register_and_login(OWNER_USER)
    response = client.get("/restaurants", headers=_auth_header(token))
    assert len(response.json()) == 0

def test_get_restaurant_by_id():
    token = register_and_login(OWNER_USER)
    restaurant = client.post("/restaurants", json=VALID_RESTAURANT, headers=_auth_header(token) ).json()

    response = client.get(f"/restaurants/{restaurant['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == restaurant["id"]

def test_get_restaurant_invalid_id():
    token = register_and_login(OWNER_USER)
    response = client.get("/restaurants/00000", headers=_auth_header(token))
    assert response.status_code == 404

#PUT tests
def test_update_restaurant_name():
    token = register_and_login(OWNER_USER)
    restaurant = client.post("/restaurants", json=VALID_RESTAURANT, headers=_auth_header(token)).json()
    response = client.put(f"/restaurants/{restaurant['id']}", json = {**VALID_RESTAURANT, "name":"Updated name"}, headers=_auth_header(token))
    assert response.status_code == 200
    assert response.json()["name"] == "Updated name"

def test_update_invalid_id():
    token = register_and_login(OWNER_USER)
    response = client.put(f"/restaurants/00000", json = {**VALID_RESTAURANT, "name":"Updated name"}, headers=_auth_header(token))
    assert response.status_code == 404

def test_restaurant_invalid_phone():
    token = register_and_login(OWNER_USER)
    restaurant = client.post("/restaurants", json=VALID_RESTAURANT, headers=_auth_header(token)).json()
    response = client.put(f"/restaurants/{restaurant['id']}", json = {**VALID_RESTAURANT, "phone":"f1234567890"}, headers=_auth_header(token))
    assert response.status_code == 422

#DELETE tests
def test_delete_restaurant():
    token = register_and_login(OWNER_USER)
    restaurant = client.post("/restaurants", json=VALID_RESTAURANT, headers=_auth_header(token)).json()
    response = client.delete(f"/restaurants/{restaurant['id']}")
    assert response.status_code == 204
    assert client.get(f"/restaurants/{restaurant['id']}", headers=_auth_header(token)).status_code == 404

def test_delete_restaurant_not_found():
    token = register_and_login(OWNER_USER)
    response = client.delete("/restaurants/00000")
    assert response.status_code == 404
#should delete menus under it
def test_delete_cascade():
    token = register_and_login(OWNER_USER)
    restaurant = client.post("/restaurants", json=VALID_RESTAURANT, headers=_auth_header(token)).json()
    menu = client.post("/menus", json = {**VALID_MENU, "restaurant_id":restaurant["id"]}, headers=_auth_header(token)).json()
    response = client.delete(f"/restaurants/{restaurant['id']}")
    assert client.get(f"/menus/{menu['id']}", headers=_auth_header(token)).status_code == 404

#Additional search feature tests
def test_search_restaurants_name_only():
    token = register_and_login(OWNER_USER)
    client.post("/restaurants", json=VALID_RESTAURANT, headers=_auth_header(token)).json()
    client.post("/restaurants", json=VALID_RESTAURANT, headers=_auth_header(token)).json()

    response = client.get("/restaurants/search?name=tEst+RestauranT")
    assert response.status_code == 200
    assert len(response.json()) == 2

def test_search_restaurants_cuisine_only():
    token = register_and_login(OWNER_USER)
    client.post("/restaurants", json=VALID_RESTAURANT, headers=_auth_header(token)).json()
    client.post("/restaurants", json=VALID_RESTAURANT, headers=_auth_header(token)).json()

    response = client.get("/restaurants/search?cuisine=pizza", headers=_auth_header(token))
    assert response.status_code == 200
    assert len(response.json()) == 2

def test_search_name_and_cuisine():
    token = register_and_login(OWNER_USER)
    client.post("/restaurants", json=VALID_RESTAURANT, headers=_auth_header(token)).json()
    client.post("/restaurants", json=VALID_RESTAURANT, headers=_auth_header(token)).json()

    response = client.get("/restaurants/search?name=test+restaurant&cuisine=italian")
    assert response.status_code == 200
    assert len(response.json()) == 2

def test_search_restaurants_no_matches():
    token = register_and_login(OWNER_USER)
    client.post("/restaurants", json=VALID_RESTAURANT, headers=_auth_header(token)).json()
    client.post("/restaurants", json=VALID_RESTAURANT, headers=_auth_header(token)).json()

    response = client.get("/restaurants/search?name=abc")
    assert response.status_code == 200
    assert len(response.json()) == 0

def test_search_restaurants_one_matches():
    token = register_and_login(OWNER_USER)
    client.post("/restaurants", json=VALID_RESTAURANT, headers=_auth_header(token)).json()
    client.post("/restaurants", json=VALID_RESTAURANT, headers=_auth_header(token)).json()

    response = client.get("/restaurants/search?name=abc&cuisine=pizza")
    assert response.status_code == 200
    assert len(response.json()) == 0

def test_search_restaurants_no_search():
    token = register_and_login(OWNER_USER)
    client.post("/restaurants", json=VALID_RESTAURANT, headers=_auth_header(token)).json()
    client.post("/restaurants", json=VALID_RESTAURANT, headers=_auth_header(token)).json()

    response = client.get("/restaurants/search")
    assert response.status_code == 200
    assert len(response.json()) == 2

def test_one_match():
    token = register_and_login(OWNER_USER)
    client.post("/restaurants", json=VALID_RESTAURANT, headers=_auth_header(token)).json()
    client.post("/restaurants", json={**VALID_RESTAURANT, "name": "restaurant 2"}, headers=_auth_header(token)).json()

    response = client.get("/restaurants/search?name=restaurant+2")
    assert response.status_code == 200
    assert len(response.json()) == 1

def test_pagination():
    token = register_and_login(OWNER_USER)
    for i in range(1, 11):
        client.post("/restaurants", json={**VALID_RESTAURANT, "name": f"restaurant{i}"}, headers=_auth_header(token)).json()
    
    response = client.get("/restaurants/search?limit=5&offset=5")
    assert response.status_code == 200
    assert len(response.json()) == 5
    assert response.json()[0]["name"] == "restaurant6"
    assert response.json()[4]["name"] == "restaurant10"

def test_filtered_pagination():
    token = register_and_login(OWNER_USER)
    for i in range(1, 11):
        client.post("/restaurants", json={**VALID_RESTAURANT, "name": f"restaurant"}, headers=_auth_header(token)).json()
    for i in range(1, 11):
        client.post("/restaurants", json=VALID_RESTAURANT, headers=_auth_header(token)).json()

    response = client.get("/restaurants/search?name=restaurant&limit=2&offset=9")
    assert response.status_code == 200
    assert len(response.json()) == 2
