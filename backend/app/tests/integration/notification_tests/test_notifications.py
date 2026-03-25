from fastapi.testclient import TestClient
from unittest.mock import patch
from main import app

client = TestClient(app)

VALID_DELIVERY = {
    "id": "1",
    "order_id": "101",
    "pickup_address": "Pickup",
    "dropoff_address": "Dropoff",
    "status": "pending",
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
}

VALID_NOTIFICATION = {
    "id": "1",
    "delivery_id": "1",
    "type": "delivery_notification",
    "message": "Delivery 1 has been created for order 101",
    "read": False
}


def test_post_valid_notification(test_delivery):
    response = client.post("/notifications/", json=test_delivery, params={"notification_type": "delivery_created"})
    assert response.status_code == 200
    data = response.json()
    assert data["delivery_id"] == test_delivery["id"]
    assert data["type"] == "delivery_created"
    assert "id" in data

def test_post_invalid_notification_type():
    response = client.post("/notifications/", json = VALID_DELIVERY,params={"notification_type" : "INVALID_TYPE"})
    assert response.status_code == 422
    
def test_post_missing_delivery_body():
    response = client.post("/notifications/", json = {},params={"notification_type" : "DELIVERY_CREATED"})
    assert response.status_code == 422
    
    

def test_get_notifications(test_notification):
    response = client.get(f"/notifications/{test_notification['delivery_id']}")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    
def test_get_notifications_empty():
    response = client.get("/notifications/9999999")
    assert response.status_code == 200
    assert response.json() == []

    
    
    
def test_mark_as_read(test_notification):
    response = client.patch(f"/notifications/{test_notification['delivery_id']}/{test_notification['id']}/read")
    assert response.status_code == 200
    assert response.json()["read"] == True
    
def test_mark_as_read_invalid_notification_id(test_notification):
    response = client.patch(f"/notifications/{test_notification['delivery_id']}/9999/read")
    assert response.status_code == 404
    
def test_mark_as_read_invalid_delivery_id(test_notification):
    response = client.patch(f"/notifications/9999999/1/read")
    assert response.status_code == 404
    


def test_delete_notification(test_notification):
    response = client.delete(f"/notifications/{test_notification['delivery_id']}/{test_notification['id']}")
    assert response.status_code == 200
    assert "deleted" in response.json()["message"]
    
def test_delete_notification_invalid_notification_id(test_notification):
    response = client.delete(f"/notifications/{test_notification['delivery_id']}/999999")
    assert response.status_code == 404
    
def test_delete_notification_invalid_delivery_id(test_notification):
    response = client.delete(f"/notifications/9999999/1")
    assert response.status_code == 404
    
def test_delete_notification_removes_proper(test_notification):
    client.delete(f"/notifications/{test_notification['delivery_id']}/{test_notification['id']}")
    remaining = client.get(f"/notifications/{test_notification["delivery_id"]}").json()
    assert not any(n["id"] == test_notification["id"] for n in remaining)
    