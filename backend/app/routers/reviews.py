from fastapi import APIRouter, Depends, status
from typing import List, Optional
from schemas.review import Review, ReviewCreate, RatingSummary, RestaurantRatingsView
from schemas.auth import UserResponse
from services.auth_dependencies import require_roles
from services.reviews_service import create_review, get_reviews_by_restaurant, get_rating_summary, get_restaurant_ratings_view

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.post("", response_model=Review, status_code=status.HTTP_201_CREATED)
def post_review(
    payload: ReviewCreate,
    current_user: UserResponse = Depends(require_roles("user")),
):
    return create_review(payload, current_user.id)


@router.get("/restaurant/{restaurant_id}", response_model=List[Review])
def get_restaurant_reviews(restaurant_id: int, sort: Optional[str] = None):
    return get_reviews_by_restaurant(restaurant_id, sort)


@router.get("/restaurant/{restaurant_id}/summary", response_model=RatingSummary)
def get_restaurant_rating_summary(restaurant_id: int):
    return get_rating_summary(restaurant_id)


@router.get("/restaurant/{restaurant_id}/view", response_model=RestaurantRatingsView)
def get_restaurant_ratings(restaurant_id: int, sort: Optional[str] = None):
    return get_restaurant_ratings_view(restaurant_id, sort)
