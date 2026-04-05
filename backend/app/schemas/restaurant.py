
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime

class RestaurantCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=50)
    address: str = Field(..., min_length=5, max_length=50)
    description: str = Field(..., min_length=10, max_length=300)
    phone: str = Field(..., pattern=r'^\+?[0-9]{7,15}$')
    rating: Optional[int] = Field(..., ge=0, le=5)
    tags: List[str] = Field(default=[], max_length=10)
    opening_hours: List[str] = Field(..., max_length=7, min_length=7)
    closing_hours: List[str] = Field(..., max_length=7, min_length=7)
    max_prep_time_minutes: int = Field(..., ge=1, le=60)

@field_validator("opening_hours", "closing_hours")
def validate_time_format(cls, value: List[str]):
    for v in value:
        if v in ("", "closed"):
            continue
        try:
            datetime.strptime(v, "%H:%M")
        except ValueError:
            raise ValueError("Format must be HH:MM, empty, or 'closed'")
    return value

class Restaurant(RestaurantCreate):
    id: str
    owner_id: Optional[str] = None

class RestaurantUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=50)
    address: Optional[str] = Field(None, min_length=5, max_length=50)
    description: Optional[str] = Field(None, min_length=10, max_length=300)
    phone: Optional[str] = Field(None, pattern=r'^\+?[0-9]{7,15}$')
    rating: Optional[int] = Field(None, ge=0, le=5)
    tags: Optional[List[str]] = Field(default=[], max_length=10)
    owner_id: Optional[str] = None
    opening_hours: Optional[List[str]] = Field(default=None, max_length=7, min_length=7)
    closing_hours: Optional[List[str]] = Field(default=None, max_length=7, min_length=7)
    max_prep_time_minutes: Optional[int] = Field(None, ge=1, le=60)
    