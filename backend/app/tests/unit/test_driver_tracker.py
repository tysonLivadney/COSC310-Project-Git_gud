from schemas.location import Location
from services.driver_tracker import DriverTracker

def test_update_and_get_driver_location():
    tracker = DriverTracker()
    tracker.update_driver_location(
        1,
        Location(latitude=49.25, longitude=-123.10, address="Burnaby")
    )
    saved = tracker.get_driver_location(1)
    assert saved is not None
    assert saved.latitude == 49.25
    assert saved.longitude == -123.10
    assert saved.address == "Burnaby"

def test_get_driver_location_not_found():
    tracker = DriverTracker()
    saved = tracker.get_driver_location(999)
    assert saved is None