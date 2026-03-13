from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

VALID_DRIVER = {
    "id": 1,
    "name": "John Smith",
    "phone": "+123456789",
    "status": "online"
}

def test_create_delivery():
    response = client.post("/deliveries/", params={
        "order_id": 101,
        "pickup_address": "123 Pickup St",
        "dropoff_address": "456 Dropoff Ave"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["order_id"] == 101
    assert data["status"] == "pending"
    assert "id" in data

def test_create_delivery_missing_fields():
    response = client.post("/deliveries/", params={"order_id": 101})
    assert response.status_code == 422


def test_get_all_deliveries():
    response = client.get("/deliveries/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_all_deliveries_empty():
    response = client.get("/deliveries/")
    assert response.status_code == 200
    assert response.json() == []

def test_get_delivery(test_delivery):
    response = client.get(f"/deliveries/{test_delivery['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == test_delivery["id"]

def test_get_delivery_not_found():
    response = client.get("/deliveries/99999")
    assert response.status_code == 404

def test_get_delivery_invalid_id():
    response = client.get("/deliveries/not-an-int")
    assert response.status_code == 422





def test_delete_delivery(test_delivery):
    response = client.delete(f"/deliveries/{test_delivery['id']}")
    assert response.status_code == 200
    assert client.get(f"/deliveries/{test_delivery['id']}").status_code == 404

def test_delete_delivery_not_found():
    response = client.delete("/deliveries/99999")
    assert response.status_code == 404





def test_assign_driver(test_delivery):
    response = client.patch(f"/deliveries/{test_delivery['id']}/assign", json=VALID_DRIVER)
    assert response.status_code == 200
    assert response.json()["status"] == "assigned"
    assert response.json()["driver"]["id"] == VALID_DRIVER["id"]

def test_assign_driver_not_found():
    response = client.patch("/deliveries/99999/assign", json=VALID_DRIVER)
    assert response.status_code == 404




def test_pickup_delivery(test_assigned_delivery):
    response = client.patch(f"/deliveries/{test_assigned_delivery['id']}/pickup")
    assert response.status_code == 200
    assert response.json()["status"] == "picked_up"

def test_pickup_delivery_invalid_transition(test_delivery):
    response = client.patch(f"/deliveries/{test_delivery['id']}/pickup")
    assert response.status_code == 400

def test_pickup_delivery_not_found():
    response = client.patch("/deliveries/99999/pickup")
    assert response.status_code == 404




def test_start_transit(test_picked_up_delivery):
    response = client.patch(f"/deliveries/{test_picked_up_delivery['id']}/transit")
    assert response.status_code == 200
    assert response.json()["status"] == "in_transit"

def test_start_transit_invalid_transition(test_delivery):
    response = client.patch(f"/deliveries/{test_delivery['id']}/transit")
    assert response.status_code == 400

def test_start_transit_not_found():
    response = client.patch("/deliveries/99999/transit")
    assert response.status_code == 404




def test_complete_delivery(test_in_transit_delivery):
    response = client.patch(f"/deliveries/{test_in_transit_delivery['id']}/complete")
    assert response.status_code == 200
    assert response.json()["status"] == "delivered"

def test_complete_delivery_invalid_transition(test_delivery):
    response = client.patch(f"/deliveries/{test_delivery['id']}/complete")
    assert response.status_code == 400

def test_complete_delivery_not_found():
    response = client.patch("/deliveries/99999/complete")
    assert response.status_code == 404




def test_cancel_delivery(test_delivery):
    response = client.patch(f"/deliveries/{test_delivery['id']}/cancel")
    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"

def test_cancel_completed_delivery(test_in_transit_delivery):
    client.patch(f"/deliveries/{test_in_transit_delivery['id']}/complete")
    response = client.patch(f"/deliveries/{test_in_transit_delivery['id']}/cancel")
    assert response.status_code == 400

def test_cancel_delivery_not_found():
    response = client.patch("/deliveries/99999/cancel")
    assert response.status_code == 404