from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_confirm_order_integration_success():
    order_payload = {
        "restaurant_id": "rest-123",
        "customer_id": "cust-123",
        "items": [
            {
                "food_item": "Burger",
                "quantity": 2,
                "unit_price": 12.5
            }
        ]
    }
    order_response = client.post("/orders", json=order_payload)
    assert order_response.status_code in (200, 201), order_response.text
    order_data = order_response.json()
    order_id = order_data["id"]

    customer_location_payload = {
        "user_id": "cust-123",
        "latitude": 49.2827,
        "longitude": -123.1207,
        "address": "customer address"
    }
    customer_location_response = client.post(
        "/location/users",
        json=customer_location_payload
    )
    assert customer_location_response.status_code == 200, customer_location_response.text

    restaurant_location_payload = {
        "restaurant_id": "rest-123",
        "latitude": 49.2800,
        "longitude": -123.1100,
        "address": "restaurant address"
    }
    restaurant_location_response = client.post(
        "/location/restaurants",
        json=restaurant_location_payload
    )
    assert restaurant_location_response.status_code == 200, restaurant_location_response.text
    confirm_payload = {
        "payment_info": {
            "card_number": "4242424242424242",
            "expiry": "12/28",
            "cvv": "123"
        }
    }

    confirm_response = client.post(
        f"/orders/{order_id}/confirm",
        json=confirm_payload
    )
    assert confirm_response.status_code == 200, confirm_response.text
    confirm_data = confirm_response.json()
    assert confirm_data["order_id"] == order_id
    assert confirm_data["status"] == "confirmed"
    assert confirm_data["payment"]["status"] == "approved"
    assert "distance_km" in confirm_data
    assert "subtotal" in confirm_data
    assert "tax" in confirm_data
    assert "delivery_fee" in confirm_data
    assert "total" in confirm_data
    assert confirm_data["province"] == "BC"

    get_order_response = client.get(f"/orders/{order_id}")
    assert get_order_response.status_code == 200, get_order_response.text
    saved_order = get_order_response.json()
    assert saved_order["status"] == "confirmed"
    assert saved_order["confirmed_at"] is not None