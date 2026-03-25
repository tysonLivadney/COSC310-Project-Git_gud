from schemas.location import Location
from repositories.locations_repo import load_all, save_all

class DriverTracker:
    def update_driver_location(self, driver_id: int, location: Location) -> dict:
        data = load_all()
        data["drivers"][str(driver_id)] = location.model_dump()
        save_all(data)
        return data["drivers"][str(driver_id)]
    
    def get_driver_location(self, driver_id: int):
        data = load_all()
        driver_data = data["drivers"].get(str(driver_id))
        if driver_data is None:
            return None
        return Location(**driver_data)