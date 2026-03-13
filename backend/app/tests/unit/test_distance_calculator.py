from schemas.location import Location
from services.distance_calculator import DistanceCalculator

def test_calculate_distance_same_point():
    loc = Location(latitude=49.2827, longitude=-123.1207, address="Same Place")
    distance = DistanceCalculator.calculate_distance_km(loc, loc)
    assert round(distance, 2) == 0.0

def test_calculate_distance_different_points():
    loc1 = Location(latitude=49.2827, longitude=-123.1207, address="Test Point A")
    loc2 = Location(latitude=49.25, longitude=-123.10, address="Test Point B")
    distance = DistanceCalculator.calculate_distance_km(loc1, loc2)
    assert distance > 0