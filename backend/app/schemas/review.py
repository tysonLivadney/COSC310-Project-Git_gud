from pydantic import BaseModel, Field
from typing import Optional


class ReviewCreate(BaseModel):
    order_id: str
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None


class Review(BaseModel):
    id: str
    order_id: str
    restaurant_id: int
    user_id: str
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None
    created_at: str
