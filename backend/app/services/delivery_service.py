from schemas import Delivery, DeliveryStatus, Driver
from datetime import datetime
from typing import Optional
from repositories import DeliveryRepo

repo = DeliveryRepo()
_next_delivery_id = 1

def create_delivery(order_id: int, pickup_address: str, dropoff_address: str) -> Delivery:
    global _next_delivery_id
    delivery = Delivery(
        id= _next_delivery_id,
        order_id = order_id,
        pickup_address=pickup_address,
        dropoff_address=dropoff_address,
        )
    repo.save(delivery)
    _next_delivery_id += 1
    return delivery

def get_delivery(delivery_id: int) -> Delivery:
    delivery = repo.get(delivery_id)
    if not delivery:
        raise KeyError(f"Delivery {delivery_id} not found")
    return delivery

def get_all_deliveries() -> list[Delivery]:
    return repo.get_all()

def delete_delivery(delivery_id: int) -> None:
    get_delivery(delivery_id)
    del repo.delete(delivery_id)

def assign_driver(delivery_id:int, driver: Driver) -> Delivery:
    delivery = get_delivery(delivery_id)
    _validate_transition(delivery.status,DeliveryStatus.ASSIGNED)
    delivery.driver = driver
    delivery.status = DeliveryStatus.ASSIGNED
    delivery.updated_at = datetime.now()
    repo.save(delivery)
    return delivery
    
def pickup_delivery(delivery_id: int) -> Delivery:
    delivery = get_delivery(delivery_id)
    _validate_transition(delivery.status, DeliveryStatus.PICKED_UP)
    delivery.status = DeliveryStatus.PICKED_UP
    delivery.updated_at = datetime.now()
    repo.save(delivery)
    return delivery

def start_transit(delivery_id: int) -> Delivery:
    delivery = get_delivery(delivery_id)
    _validate_transition(delivery.status, DeliveryStatus.IN_TRANSIT)
    delivery.status = DeliveryStatus.IN_TRANSIT
    delivery.updated_at = datetime.now()
    repo.save(delivery)
    return delivery

def complete_delivery(delivery_id: int) -> Delivery:
    delivery = get_delivery(delivery_id)
    _validate_transition(delivery.status, DeliveryStatus.DELIVERED)
    delivery.status = DeliveryStatus.DELIVERED
    delivery.updated_at = datetime.now()
    repo.save(delivery)
    return delivery
    
def cancel_delivery(delivery_id: int) -> Delivery:
    delivery = get_delivery(delivery_id)
    if delivery.status == DeliveryStatus.DELIVERED:
        raise ValueError("Cannot cancel completed delivery")
    delivery.status = DeliveryStatus.CANCELLED
    delivery.updated_at = datetime.now()
    repo.save(delivery)
    return delivery

_valid_transitions = {
    DeliveryStatus.PENDING: [DeliveryStatus.ASSIGNED, DeliveryStatus.CANCELLED],
    DeliveryStatus.ASSIGNED: [DeliveryStatus.PICKED_UP, DeliveryStatus.CANCELLED],
    DeliveryStatus.PICKED_UP: [DeliveryStatus.IN_TRANSIT, DeliveryStatus.CANCELLED],
    DeliveryStatus.IN_TRANSIT: [DeliveryStatus.DELIVERED, DeliveryStatus.CANCELLED],
    DeliveryStatus.DELIVERED: [],
    DeliveryStatus.CANCELLED: [],
}

def _validate_transition(current: DeliveryStatus, next: DeliveryStatus) -> None:
    if next not in _valid_transitions[current]:
        raise ValueError(f"Cannot transition from {current} to {next}")