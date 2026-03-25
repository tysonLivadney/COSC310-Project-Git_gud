from pydantic import BaseModel, Field
from typing import Optional


class DriverProfileCreate(BaseModel):
    phone: str = Field(..., min_length=7, max_length=15)
    vehicle_type: str = Field(..., min_length=2, max_length=50)
    license_plate: str = Field(..., min_length=2, max_length=15)


class DriverProfile(BaseModel):
    user_id: str
    name: str
    phone: str
    vehicle_type: str
    license_plate: str
    available: bool = False


class DriverProfileUpdate(BaseModel):
    phone: Optional[str] = None
    vehicle_type: Optional[str] = None
    license_plate: Optional[str] = None
    available: Optional[bool] = None
