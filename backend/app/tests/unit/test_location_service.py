from schemas.location import Location
from services.location_service import LocationService

def test_update_and_get_user_location():
    service = LocationService()
    service.update_user_location(
        1,
        Location(latitude=49.2827, longitude=-123.1207, address="Vancouver")
    )
    saved = service.get_user_location(1)
    assert saved is not None
    assert saved.latitude == 49.2827
    assert saved.longitude == -123.1207
    assert saved.address == "Vancouver"

def test_update_and_get_restaurant_location():
    service = LocationService()
    service.update_restaurant_location(
        100,
        Location(latitude=49.263, longitude=-123.138, address="Restaurant Area")
    )
    saved = service.get_restaurant_location(100)
    assert saved is not None
    assert saved.latitude == 49.263
    assert saved.longitude == -123.138
    assert saved.address == "Restaurant Area"

def test_get_user_location_not_found():
    service = LocationService()
    saved = service.get_user_location(999)
    assert saved is None

def test_get_distance_user_to_restaurant():
    service = LocationService()
    service.update_user_location(
        1,
        Location(latitude=49.2827, longitude=-123.1207, address="User")
    )
    service.update_restaurant_location(
        100,
        Location(latitude=49.263, longitude=-123.138, address="Restaurant")
    )
    distance = service.get_distance_user_to_restaurant(1, 100)
    
    assert distance is not None
    assert distance > 0