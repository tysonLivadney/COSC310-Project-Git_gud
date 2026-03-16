from pydantic import BaseModel, Field, field_validator
from typing import List, Optional


class ReviewCreate(BaseModel):
    order_id: str
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None

    @field_validator("comment")
    @classmethod
    def normalize_comment(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped if stripped else None


class Review(BaseModel):
    id: str
    order_id: str
    restaurant_id: int
    user_id: str
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None
    created_at: str


class RatingSummary(BaseModel):
    restaurant_id: int
    average_rating: float
    total_reviews: int


class RestaurantRatingsView(BaseModel):
    restaurant_id: int
    average_rating: float
    total_reviews: int
    reviews: List[Review]
