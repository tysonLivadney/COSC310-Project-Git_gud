import pytest
from unittest.mock import patch
from fastapi import HTTPException
from schemas import Delivery,DeliveryStatus,Driver, DriverStatus
from services import delivery_service

VALID_DRIVER = Driver(
    id="1",
    name="John Smith",
    phone="+123456789",
    status=DriverStatus.ONLINE
)

def test_create_delivery():
    delivery = delivery_service.create_delivery("100","Pickup","Dropoff")
    assert delivery.order_id == "100"
    assert delivery.pickup_address == "Pickup"
    assert delivery.dropoff_address == "Dropoff"
    assert delivery.status == DeliveryStatus.PENDING
    assert delivery.id is not None
    


def test_get_delivery():
    created = delivery_service.create_delivery("100","Pickup","Dropoff")
    fetched = delivery_service.get_delivery(created.id)
    assert fetched.id == created.id
    assert fetched.order_id == "100"
    
def test_get_delivery_not_found():
    with pytest.raises(KeyError):
        delivery_service.get_delivery("9999999")
        
def test_get_all_deliveries_empty():
    assert delivery_service.get_all_deliveries() == []

def test_get_all_deliveries():
    d1 = delivery_service.create_delivery("101","Pickup1","Dropoff1")
    d2 = delivery_service.create_delivery("102","Pickup2","Dropoff2")
    assert len(delivery_service.get_all_deliveries()) == 2



def test_delete_delivery():
    delivery = delivery_service.create_delivery("100","Pickup","Dropoff")
    delivery_service.delete_delivery(delivery.id)
    with pytest.raises(KeyError):
        delivery_service.get_delivery(delivery.id)
        
def test_delete_delivery_not_found():
    with pytest.raises(KeyError):
        delivery_service.delete_delivery("9999999")
        


def test_assign_driver():
    delivery = delivery_service.create_delivery("100","Pickup","Dropoff")
    updated = delivery_service.assign_driver(delivery.id, VALID_DRIVER)
    assert updated.status == DeliveryStatus.ASSIGNED
    assert updated.driver.id == VALID_DRIVER.id
    
def test_assign_driver_not_found():
    with pytest.raises(KeyError):
        delivery_service.assign_driver("9999999", VALID_DRIVER)
        
def test_assign_driver_invalid_transition():
    delivery = delivery_service.create_delivery("100","Pickup","Dropoff")
    delivery_service.cancel_delivery(delivery.id)
    with pytest.raises(ValueError):
        delivery_service.assign_driver(delivery.id, VALID_DRIVER)



def test_pickup_delivery():
    delivery = delivery_service.create_delivery("100","Pickup","Dropoff")
    delivery_service.assign_driver(delivery.id, VALID_DRIVER)
    updated = delivery_service.pickup_delivery(delivery.id, "1")
    assert updated.status == DeliveryStatus.PICKED_UP

def test_pickup_delivery_not_found():
    with pytest.raises(KeyError):
        delivery_service.pickup_delivery("99999", "1")

def test_pickup_delivery_invalid_transition():
    delivery = delivery_service.create_delivery("100","Pickup","Dropoff")
    with pytest.raises(HTTPException) as exc_info:
        delivery_service.pickup_delivery(delivery.id, "1")
    assert exc_info.value.status_code == 403
        


def test_start_transit():
    delivery = delivery_service.create_delivery("100","Pickup","Dropoff")
    delivery_service.assign_driver(delivery.id, VALID_DRIVER)
    delivery_service.pickup_delivery(delivery.id, "1")
    updated = delivery_service.start_transit(delivery.id, "1")
    assert updated.status == DeliveryStatus.IN_TRANSIT

def test_start_transit_not_found():
    with pytest.raises(KeyError):
        delivery_service.start_transit("99999", "1")

def test_start_transit_invalid_transition():
    delivery = delivery_service.create_delivery("100","Pickup","Dropoff")
    with pytest.raises(HTTPException) as exc_info:
        delivery_service.start_transit(delivery.id, "1")
    assert exc_info.value.status_code == 403



def test_complete_delivery():
    delivery = delivery_service.create_delivery("100","Pickup","Dropoff")
    delivery_service.assign_driver(delivery.id, VALID_DRIVER)
    delivery_service.pickup_delivery(delivery.id, "1")
    delivery_service.start_transit(delivery.id, "1")
    updated = delivery_service.complete_delivery(delivery.id, "1")
    assert updated.status == DeliveryStatus.DELIVERED

def test_complete_delivery_not_found():
    with pytest.raises(KeyError):
        delivery_service.complete_delivery("99999", "1")

def test_complete_delivery_invalid_transition():
    delivery = delivery_service.create_delivery("100","Pickup","Dropoff")
    with pytest.raises(HTTPException) as exc_info:
        delivery_service.complete_delivery(delivery.id, "1")
    assert exc_info.value.status_code == 403
        
        
        
def test_cancel_delivery():
    delivery = delivery_service.create_delivery("100","Pickup","Dropoff")
    updated = delivery_service.cancel_delivery(delivery.id)
    assert updated.status == DeliveryStatus.CANCELLED
    
def test_cancel_completed_delivery():
    delivery = delivery_service.create_delivery("100","Pickup","Dropoff")
    delivery_service.assign_driver(delivery.id, VALID_DRIVER)
    delivery_service.pickup_delivery(delivery.id, "1")
    delivery_service.start_transit(delivery.id, "1")
    delivery_service.complete_delivery(delivery.id, "1")
    with pytest.raises(ValueError):
        delivery_service.cancel_delivery(delivery.id)
        
def test_cancel_delivery_not_found():
    with pytest.raises(KeyError):
        delivery_service.cancel_delivery("999999")
        
        
