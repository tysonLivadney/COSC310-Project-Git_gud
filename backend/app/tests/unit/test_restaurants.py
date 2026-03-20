from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

VALID_RESTAURANT = {
    "name": "Test Restaurant",
    "address": " 123 Address ", 
    "description": "Example of a description.",
    "phone": "+123456789",
    "rating": 5,
    "tags": ["italian", "pizza"],
    "estimated_delivery_time": 10
}

VALID_MENU = {
    "name": "Test Menu",
    "description": "Test menu description that is long enough.",
}


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

def test_name_too_long():
    invalid_restaurant = {**VALID_RESTAURANT, "name": "123456789012345678901234567890123456789012345678901"}
    response = client.post("/restaurants", json=invalid_restaurant)
    assert response.status_code == 422

def test_post_invalid_phone():
    invalid_restaurant = {**VALID_RESTAURANT, "phone": "a123456789"} 
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

def test_get_restaurants(): 
    client.post("/restaurants", json=VALID_RESTAURANT)
    client.post("/restaurants", json=VALID_RESTAURANT)

    response = client.get("/restaurants")
    assert response.status_code == 200
    assert len(response.json()) == 2

def test_get_restaurants_empty_file():
    response = client.get("/restaurants")
    assert len(response.json()) == 0 

def test_get_restaurant_by_id():
    testaurant = client.post("/restaurants", json=VALID_RESTAURANT).json()

    response = client.get(f"/restaurants/{testaurant['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == testaurant["id"]

def test_get_restaurant_invalid_id():
    response = client.get("/restaurants/00000")
    assert response.status_code == 404

#PUT tests
def test_update_restaurant_name():
    restaurant = client.post("/restaurants", json=VALID_RESTAURANT).json()
    response = client.put(f"/restaurants/{restaurant['id']}", json = {**VALID_RESTAURANT, "name":"Updated name"})
    assert response.status_code == 200
    assert response.json()["name"] == "Updated name"

def test_update_invalid_id():
    restaurant = client.post("/restaurants", json=VALID_RESTAURANT).json()
    response = client.put(f"/restaurants/00000", json = {**VALID_RESTAURANT, "name":"Updated name"})
    assert response.status_code == 404

def test_restaurant_invalid_phone():
    restaurant = client.post("/restaurants", json=VALID_RESTAURANT).json()
    response = client.put(f"/restaurants/{restaurant['id']}", json = {**VALID_RESTAURANT, "phone":"f1234567890"})
    assert response.status_code == 422

#DELETE tests
def test_delete_restaurant():
    restaurant = client.post("/restaurants", json=VALID_RESTAURANT).json()
    response = client.delete(f"/restaurants/{restaurant['id']}")
    assert response.status_code == 204
    assert client.get(f"/restaurants/{restaurant['id']}").status_code == 404

def test_delete_restaurant_not_found():
    response = client.delete("/restaurants/00000")
    assert response.status_code == 404
#should delete menus under it
def test_delete_cascade():
    restaurant = client.post("/restaurants", json=VALID_RESTAURANT).json()
    menu = client.post("/menus", json = {**VALID_MENU, "restaurant_id":restaurant["id"]}).json()
    response = client.delete(f"/restaurants/{restaurant['id']}")
    assert client.get(f"/menus/{menu['id']}").status_code == 404

#Additional search feature tests
def test_search_restaurants_name_only():
    client.post("/restaurants", json=VALID_RESTAURANT).json()
    client.post("/restaurants", json=VALID_RESTAURANT).json()

    response = client.get("/restaurants/search?name=tEst+RestauranT")
    assert response.status_code == 200
    assert len(response.json()) == 2

def test_search_restaurants_cuisine_only():
    client.post("/restaurants", json=VALID_RESTAURANT).json()
    client.post("/restaurants", json=VALID_RESTAURANT).json()

    response = client.get("/restaurants/search?cuisine=pizza")
    assert response.status_code == 200
    assert len(response.json()) == 2

def test_search_name_and_cuisine():
    client.post("/restaurants", json=VALID_RESTAURANT).json()
    client.post("/restaurants", json=VALID_RESTAURANT).json()

    response = client.get("/restaurants/search?name=test+restaurant&cuisine=italian")
    assert response.status_code == 200
    assert len(response.json()) == 2

def test_search_restaurants_no_matches():
    client.post("/restaurants", json=VALID_RESTAURANT).json()
    client.post("/restaurants", json=VALID_RESTAURANT).json()

    response = client.get("/restaurants/search?name=abc")
    assert response.status_code == 200
    assert len(response.json()) == 0

def test_search_restaurants_one_matches():
    client.post("/restaurants", json=VALID_RESTAURANT).json()
    client.post("/restaurants", json=VALID_RESTAURANT).json()

    response = client.get("/restaurants/search?name=abc&cuisine=pizza")
    assert response.status_code == 200
    assert len(response.json()) == 0

def test_search_restaurants_no_search():
    client.post("/restaurants", json=VALID_RESTAURANT).json()
    client.post("/restaurants", json=VALID_RESTAURANT).json()

    response = client.get("/restaurants/search")
    assert response.status_code == 200
    assert len(response.json()) == 2

def test_one_match():
    client.post("/restaurants", json=VALID_RESTAURANT)
    client.post("/restaurants", json={**VALID_RESTAURANT, "name": "restaurant 2"})

    response = client.get("/restaurants/search?name=restaurant+2")
    assert response.status_code == 200
    assert len(response.json()) == 1

def test_pagination():
    for i in range(1, 11):
        client.post("/restaurants", json={**VALID_RESTAURANT, "name": f"restaurant{i}"})
    
    response = client.get("/restaurants/search?limit=5&offset=5") #return 5-10
    assert response.status_code == 200
    assert len(response.json()) == 5
    assert response.json()[0]["name"] == "restaurant6"
    assert response.json()[4]["name"] == "restaurant10"

def test_filtered_pagination():
    for i in range(1, 11):
        client.post("/restaurants", json={**VALID_RESTAURANT, "name": f"restaurant"})
    for i in range(1, 11):
        client.post("/restaurants", json=VALID_RESTAURANT)

    response = client.get("/restaurants/search?name=restaurant&limit=2&offset=9")
    assert response.status_code == 200
    assert len(response.json()) == 2 #inclusive of offset