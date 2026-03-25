from schemas.location import Location
from services.distance_calculator import DistanceCalculator
from services.driver_tracker import DriverTracker
from repositories.locations_repo import load_all, save_all

class LocationService:
    def __init__(self):
        self.driver_tracker = DriverTracker()

    def update_user_location(self, user_id: int, location: Location) -> dict:
        data = load_all()
        data["users"][str(user_id)] = location.model_dump()
        save_all(data)
        return data["users"][str(user_id)]
    
    def get_user_location(self, user_id: str):
        data = load_all()
        user_data = data["users"].get(str(user_id))
        if user_data is None:
            return None
        return Location(**user_data)
    
    def update_restaurant_location(self, restaurant_id: int, location: Location) -> dict:
        data = load_all()
        data["restaurants"][str(restaurant_id)] = location.model_dump()
        save_all(data)
        return data["restaurants"][str(restaurant_id)]
    
    def get_restaurant_location(self, restaurant_id: str):
        data = load_all()
        restaurant_data = data["restaurants"].get(str(restaurant_id))
        if restaurant_data is None:
            return None
        return Location(**restaurant_data)

    def update_driver_location(self, driver_id: int, location: Location) -> dict:
        return self.driver_tracker.update_driver_location(driver_id, location)

    def get_driver_location(self, driver_id: int):
        return self.driver_tracker.get_driver_location(driver_id)

    def calculate_distance_between(self, from_location: Location, to_location: Location) -> float:
        return DistanceCalculator.calculate_distance_km(from_location, to_location)

    def get_distance_user_to_restaurant(self, user_id: int, restaurant_id: int):
        user_location = self.get_user_location(user_id)
        restaurant_location = self.get_restaurant_location(restaurant_id)
        if user_location is None or restaurant_location is None:
            return None
        return self.calculate_distance_between(user_location, restaurant_location)