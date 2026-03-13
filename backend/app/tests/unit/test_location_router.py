from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_post_user_location():
    response = client.post("/location/users", json={
        "user_id": 1,
        "latitude": 49.2827,
        "longitude": -123.1207,
        "address": "Vancouver"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "User location updated successfully"

def test_get_user_location():
    client.post("/location/users", json={
        "user_id": 1,
        "latitude": 49.2827,
        "longitude": -123.1207,
        "address": "Vancouver"
    })
    response = client.get("/location/users/1")
    assert response.status_code == 200
    data = response.json()
    assert data["latitude"] == 49.2827
    assert data["longitude"] == -123.1207
    assert data["address"] == "Vancouver"

def test_post_driver_location():
    response = client.post("/location/drivers", json={
        "driver_id": 1,
        "latitude": 49.25,
        "longitude": -123.10,
        "address": "Burnaby"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Driver location updated successfully"

def test_get_driver_location_not_found():
    response = client.get("/location/drivers/999")
    assert response.status_code == 404

def test_post_restaurant_location():
    response = client.post("/location/restaurants", json={
        "restaurant_id": 100,
        "latitude": 49.263,
        "longitude": -123.138,
        "address": "Restaurant Area"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Restaurant location updated successfully"

def test_get_restaurant_location():
    client.post("/location/restaurants", json={
        "restaurant_id": 100,
        "latitude": 49.263,
        "longitude": -123.138,
        "address": "Restaurant Area"
    })
    response = client.get("/location/restaurants/100")
    assert response.status_code == 200
    data = response.json()
    assert data["latitude"] == 49.263
    assert data["longitude"] == -123.138
    assert data["address"] == "Restaurant Area"

def test_post_distance():
    response = client.post("/location/distance", json={
        "from_location": {
            "latitude": 49.2827,
            "longitude": -123.1207,
            "address": "Point A"
        },
        "to_location": {
            "latitude": 49.25,
            "longitude": -123.10,
            "address": "Point B"
        }
    })
    assert response.status_code == 200
    data = response.json()
    assert "distance_km" in data
    assert data["distance_km"] > 0

def test_get_user_to_restaurant_distance():
    client.post("/location/users", json={
        "user_id": 1,
        "latitude": 49.2827,
        "longitude": -123.1207,
        "address": "User"
    })
    client.post("/location/restaurants", json={
        "restaurant_id": 100,
        "latitude": 49.263,
        "longitude": -123.138,
        "address": "Restaurant"
    })
    response = client.get("/location/users/1/restaurants/100/distance")
    assert response.status_code == 200
    data = response.json()
    assert "distance_km" in data
    assert data["distance_km"] > 0

def test_post_user_location_invalid_body():
    response = client.post("/location/users", json={
        "user_id": 1,
        "latitude": 49.2827
    })
    assert response.status_code == 422