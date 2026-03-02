from ..schemas import Delivery, Driver
from ..schemas.enums import DeliveryStatus
from datetime import datetime
from typing import Optional

deliveries: dict[int,Delivery] = {}
_next_id = 1

def create_delivery(order_id: int, pickup_address: str, dropoff_address: str) -> Delivery:
    global _next_id
    delivery = Delivery(
        id= _next_id,
        order_id = order_id,
        pickup_address=pickup_address,
        dropoff_address=dropoff_address,
        )
    deliveries[_next_id] = delivery
    _next_id += 1
    return delivery

def assign_driver(delivery_id:int, driver: Driver) -> Delivery:
    delivery = _get_delivery(delivery_id)
    _valid_transitions(delivery.status,DeliveryStatus.ASSIGNED)
    delivery.driver = driver
    delivery.status = DeliveryStatus.ASSIGNED
    delivery.updated_at = datetime.now()
    return delivery
    
def pickup_delivery(delivery_id: int) -> Delivery:
    delivery = _get_delivery(delivery_id)
    _valid_transitions(delivery.status, DeliveryStatus.PICKED_UP)
    delivery.status = DeliveryStatus.PICKED_UP
    delivery.updated_at = datetime.now()
    return delivery

def start_transit(delivery_id: int) -> Delivery:
    delivery = _get_delivery(delivery_id)
    _valid_transitions(delivery.status, DeliveryStatus.IN_TRANSIT)
    delivery.status = DeliveryStatus.IN_TRANSIT
    delivery.updated_at = datetime.now()
    return delivery

def complete_delivery(delivery_id: int) -> Delivery:
    delivery = _get_delivery(delivery_id)
    _valid_transitions(delivery.status, DeliveryStatus.DELIVERED)
    delivery.status = DeliveryStatus.DELIVERED
    delivery.updated_at = datetime.now()
    return delivery
    
def cancel_order(delivery_id: int) -> Delivery:
    delivery = _get_delivery(delivery_id)
    if delivery.status == DeliveryStatus.DELIVERED:
        raise ValueError("Cannot cancel completed delivery")
    delivery.status = DeliveryStatus.CANCELLED
    delivery.updated_at = datetime.now()
    return delivery
    
    
def _get_delivery(delivery_id: int) -> Delivery:
    delivery = deliveries.get(delivery_id)
    return delivery

_valid_transitions = {
     DeliveryStatus.PENDING: [DeliveryStatus.ASSIGNED, DeliveryStatus.CANCELLED],
    DeliveryStatus.ASSIGNED: [DeliveryStatus.PICKED_UP, DeliveryStatus.CANCELLED],
    DeliveryStatus.PICKED_UP: [DeliveryStatus.IN_TRANSIT, DeliveryStatus.CANCELLED],
    DeliveryStatus.IN_TRANSIT: [DeliveryStatus.DELIVERED, DeliveryStatus.CANCELLED],
    DeliveryStatus.DELIVERED: [],
    DeliveryStatus.CANCELLED: [],
}