from pydantic import BaseModel, Field
from typing import Optional

class Location(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    address: Optional[str] = None

class UpdateUserLocationRequest(BaseModel):
    user_id: str
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    address: Optional[str] = None

class UpdateDriverLocationRequest(BaseModel):
    driver_id: str
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    address: Optional[str] = None

class UpdateRestaurantLocationRequest(BaseModel):
    restaurant_id: str
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    address: Optional[str] = None

class DistanceRequest(BaseModel):
    from_location: Location
    to_location: Location