from services import delivery_service
from schemas import DeliveryStatus
from repositories.drivers_repo import save_all as save_drivers, load_all as load_drivers


def _make_driver(available=True):
    save_drivers([{
        "user_id": "d1",
        "name": "John",
        "phone": "+1234567890",
        "vehicle_type": "Sedan",
        "license_plate": "XYZ",
        "available": available,
    }])

def test_auto_assigns_when_driver_available():
    _make_driver()
    delivery = delivery_service.create_delivery("100", "Pickup St", "Dropoff Ave")
    assert delivery.driver is not None
    assert delivery.driver.id == "d1"
    assert delivery.status == DeliveryStatus.ASSIGNED

def test_no_driver_stays_pending():
    delivery = delivery_service.create_delivery("100", "Pickup St", "Dropoff Ave")
    assert delivery.driver is None
    assert delivery.status == DeliveryStatus.PENDING

def test_unavailable_driver_not_assigned():
    _make_driver(available=False)
    delivery = delivery_service.create_delivery("100", "Pickup St", "Dropoff Ave")
    assert delivery.driver is None

def test_driver_marked_unavailable_after_assign():
    _make_driver()
    delivery_service.create_delivery("100", "Pickup St", "Dropoff Ave")
    drivers = load_drivers()
    assert drivers[0]["available"] == False
