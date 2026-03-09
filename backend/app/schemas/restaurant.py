
from pydantic import BaseModel, Field
from typing import List, Optional

class RestaurantCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=50)
    address: str = Field(..., min_length=5, max_length=50)
    description: str = Field(..., min_length=10, max_length=300)
    phone: str = Field(..., pattern=r'^\+?[0-9]{7,15}$') #ensure correct phone format w/ regex
    rating: Optional[int] = Field(..., ge=0, le=5) #rating 1-5. When first created restaurants won't have ratings
    tags: List[str] = Field(default=[], max_length=10)
class Restaurant(RestaurantCreate):
    id: str

class RestaurantUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=50)
    address: Optional[str] = Field(None, min_length=5, max_length=50)
    description: Optional[str] = Field(None, min_length=10, max_length=300)
    phone: Optional[str] = Field(None, pattern=r'^\+?[0-9]{7,15}$')
    rating: Optional[int] = Field(None, ge=0, le=5)
    tags: Optional[List[str]] = Field(default=[], max_length=10)
    