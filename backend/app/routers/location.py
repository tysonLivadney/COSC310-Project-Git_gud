from fastapi import APIRouter, HTTPException
from schemas.location import (
    Location,
    UpdateUserLocationRequest,
    UpdateDriverLocationRequest,
    UpdateRestaurantLocationRequest,
    DistanceRequest,
)
from services.location_service import LocationService
router = APIRouter(prefix="/location", tags=["Location"])
location_service = LocationService()

@router.post("/users")
def update_user_location(request: UpdateUserLocationRequest):
    location = Location(
        latitude=request.latitude,
        longitude=request.longitude,
        address=request.address
    )
    saved = location_service.update_user_location(request.user_id, location)
    return {
        "message": "User location updated successfully",
        "location": saved
    }

@router.get("/users/{user_id}")
def get_user_location(user_id: str):
    location = location_service.get_user_location(user_id)
    if location is None:
        raise HTTPException(status_code=404, detail="User location not found")
    return location

@router.post("/drivers")
def update_driver_location(request: UpdateDriverLocationRequest):
    location = Location(
        latitude=request.latitude,
        longitude=request.longitude,
        address=request.address
    )
    saved = location_service.update_driver_location(request.driver_id, location)
    return {
        "message": "Driver location updated successfully",
        "location": saved
    }

@router.get("/drivers/{driver_id}")
def get_driver_location(driver_id: str):
    location = location_service.get_driver_location(driver_id)
    if location is None:
        raise HTTPException(status_code=404, detail="Driver location not found")
    return location

@router.post("/restaurants")
def update_restaurant_location(request: UpdateRestaurantLocationRequest):
    location = Location(
        latitude=request.latitude,
        longitude=request.longitude,
        address=request.address
    )
    saved = location_service.update_restaurant_location(request.restaurant_id, location)
    return {
        "message": "Restaurant location updated successfully",
        "location": saved
    }

@router.get("/restaurants/{restaurant_id}")
def get_restaurant_location(restaurant_id: str):
    location = location_service.get_restaurant_location(restaurant_id)
    if location is None:
        raise HTTPException(status_code=404, detail="Restaurant location not found")
    return location

@router.post("/distance")
def calculate_distance(request: DistanceRequest):
    distance = location_service.calculate_distance_between(
        request.from_location,
        request.to_location
    )
    return {"distance_km": round(distance, 2)}

@router.get("/users/{user_id}/restaurants/{restaurant_id}/distance")
def get_user_to_restaurant_distance(user_id: int, restaurant_id: int):
    distance = location_service.get_distance_user_to_restaurant(user_id, restaurant_id)
    if distance is None:
        raise HTTPException(status_code=404, detail="User or restaurant location not found")
    return {"distance_km": round(distance, 2)}
