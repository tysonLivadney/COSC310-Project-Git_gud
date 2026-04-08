from schemas import Delivery, DeliveryStatus, Driver, DriverStatus
from schemas.notifications import NotificationType
from datetime import datetime
from typing import Optional
from fastapi import HTTPException
from repositories.delivery_repo import load_all, save_all
from repositories.drivers_repo import load_all as load_all_drivers, save_all as save_all_drivers
from services import notifications_service
from services.address_resolver import resolve_delivery_addresses
from services.orders_service import complete_order
from uuid import uuid4



def create_delivery(order_id: str, pickup_address: Optional[str] = None, dropoff_address: Optional[str] = None) -> Delivery:
    deliveries = load_all()
    new_id = str(uuid4())
    if any(it.get("id") == new_id for it in deliveries):
        raise HTTPException(status_code=409, detail="ID collision; retry.")
    pickup_address, dropoff_address = resolve_delivery_addresses(order_id, pickup_address, dropoff_address)
    delivery = Delivery(
        id=new_id,
        order_id=order_id,
        pickup_address=pickup_address,
        dropoff_address=dropoff_address,
        )

    # try to auto assign an available driver
    drivers = load_all_drivers()
    for d in drivers:
        if d.get("available"):
            delivery.driver = Driver(
                id=d["user_id"],
                name=d["name"],
                phone=d["phone"],
                status=DriverStatus.BUSY,
            )
            delivery.status = DeliveryStatus.ASSIGNED
            d["available"] = False
            save_all_drivers(drivers)
            break

    deliveries = load_all()
    deliveries.append(delivery.model_dump(mode="json"))
    save_all(deliveries)
    notifications_service.notify(delivery, NotificationType.DELIVERY_CREATED)
    if delivery.status == DeliveryStatus.ASSIGNED:
        notifications_service.notify(delivery, NotificationType.DELIVERY_ASSIGNED)
    return delivery

def _update(delivery: Delivery) -> None:
    deliveries = load_all()
    for i, d in enumerate(deliveries):
        if d["id"] == delivery.id:
            deliveries[i] = delivery.model_dump(mode="json")
            break
    save_all(deliveries)

def get_delivery(delivery_id: str) -> Delivery:
    deliveries = load_all()
    for d in deliveries:
        if d["id"] == delivery_id:
            if d.get("driver"):
                d["driver"] = Driver(**d["driver"])
            return Delivery(**d)
    raise KeyError(f"Delivery {delivery_id} not found")

def get_all_deliveries() -> list[Delivery]:
    return [Delivery(**d) for d in load_all()]


def delete_delivery(delivery_id: str) -> None:
    deliveries = load_all()
    for i, d in enumerate(deliveries):
        if d["id"] == delivery_id:
            deliveries.pop(i)
            save_all(deliveries)
            return
    raise KeyError(f"Delivery {delivery_id} not found")

def _check_assigned_driver(delivery: Delivery, current_user_id: str) -> None:
    if delivery.driver is None or delivery.driver.id != current_user_id:
        raise HTTPException(status_code=403, detail="You are not the assigned driver for this delivery")

def assign_driver(delivery_id: str, driver_id: str) -> Delivery:
    drivers = load_all_drivers()
    driver_data = None
    for d in drivers:
        if d.get("user_id") == driver_id:
            driver_data = d
            break
    if not driver_data:
        raise KeyError(f"Driver {driver_id} not found")

    driver = Driver(
        id=driver_data["user_id"],
        name=driver_data["name"],
        phone=driver_data["phone"],
        status=DriverStatus.BUSY,
    )

    delivery = get_delivery(delivery_id)
    _validate_transition(delivery.status, DeliveryStatus.ASSIGNED)
    delivery.driver = driver
    delivery.status = DeliveryStatus.ASSIGNED
    delivery.updated_at = datetime.now()
    _update(delivery)
    notifications_service.notify(delivery, NotificationType.DELIVERY_ASSIGNED)
    return delivery

def pickup_delivery(delivery_id: str, current_user_id: str) -> Delivery:
    delivery = get_delivery(delivery_id)
    _check_assigned_driver(delivery, current_user_id)
    _validate_transition(delivery.status, DeliveryStatus.PICKED_UP)
    delivery.status = DeliveryStatus.PICKED_UP
    delivery.updated_at = datetime.now()
    _update(delivery)
    notifications_service.notify(delivery, NotificationType.DELIVERY_PICKED_UP)
    return delivery

def start_transit(delivery_id: str, current_user_id: str) -> Delivery:
    delivery = get_delivery(delivery_id)
    _check_assigned_driver(delivery, current_user_id)
    _validate_transition(delivery.status, DeliveryStatus.IN_TRANSIT)
    delivery.status = DeliveryStatus.IN_TRANSIT
    delivery.updated_at = datetime.now()
    _update(delivery)
    notifications_service.notify(delivery, NotificationType.DELIVERY_IN_TRANSIT)
    return delivery

def complete_delivery(delivery_id: str, current_user_id: str) -> Delivery:
    delivery = get_delivery(delivery_id)
    _check_assigned_driver(delivery, current_user_id)
    _validate_transition(delivery.status, DeliveryStatus.DELIVERED)
    delivery.status = DeliveryStatus.DELIVERED
    delivery.updated_at = datetime.now()
    _update(delivery)
    complete_order(delivery.order_id)
    notifications_service.notify(delivery, NotificationType.DELIVERY_COMPLETED)
    return delivery

def cancel_delivery(delivery_id: str) -> Delivery:
    delivery = get_delivery(delivery_id)
    _validate_transition(delivery.status, DeliveryStatus.CANCELLED)
    delivery.status = DeliveryStatus.CANCELLED
    delivery.updated_at = datetime.now()
    _update(delivery)
    notifications_service.notify(delivery, NotificationType.DELIVERY_CANCELLED)
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
