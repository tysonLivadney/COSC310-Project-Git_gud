import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable, List, Optional
from schemas.review import Review, ReviewCreate, RatingSummary, RestaurantRatingsView
from repositories.reviews_repo import load_all, save_all
from services.review_eligibility import find_order, validate_review_eligibility, check_duplicate_review


@dataclass(frozen=True)
class _SortConfig:
    key: Callable
    reverse: bool


_SORTS: dict[str, _SortConfig] = {
    "highest": _SortConfig(key=lambda r: r.rating, reverse=True),
    "lowest": _SortConfig(key=lambda r: r.rating, reverse=False),
}


def create_review(payload: ReviewCreate, user_id: str) -> Review:
    order = find_order(payload.order_id)
    validate_review_eligibility(order, user_id)
    check_duplicate_review(payload.order_id)

    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    review = Review(
        id=str(uuid.uuid4()),
        order_id=payload.order_id,
        restaurant_id=order["restaurant_id"],
        user_id=user_id,
        rating=payload.rating,
        comment=payload.comment,
        created_at=now,
    )
    reviews = load_all()
    reviews.append(review.model_dump())
    save_all(reviews)
    return review


def _sort_reviews(reviews: List[Review], sort: Optional[str]) -> List[Review]:
    config = _SORTS.get(sort or "")
    if config:
        reviews.sort(key=config.key, reverse=config.reverse)
    else:
        reviews.sort(key=lambda r: r.created_at, reverse=True)
    return reviews


def get_reviews_by_restaurant(restaurant_id: int, sort: Optional[str] = None) -> List[Review]:
    reviews = load_all()
    filtered = [Review(**r) for r in reviews if r.get("restaurant_id") == restaurant_id]
    return _sort_reviews(filtered, sort)


def get_rating_summary(restaurant_id: int) -> RatingSummary:
    reviews = load_all()
    filtered = [r for r in reviews if r.get("restaurant_id") == restaurant_id]
    total = len(filtered)
    average = round(sum(r["rating"] for r in filtered) / total, 2) if total else 0.0
    return RatingSummary(
        restaurant_id=restaurant_id,
        average_rating=average,
        total_reviews=total,
    )


def get_restaurant_ratings_view(restaurant_id: int, sort: Optional[str] = None) -> RestaurantRatingsView:
    summary = get_rating_summary(restaurant_id)
    reviews = get_reviews_by_restaurant(restaurant_id, sort)
    return RestaurantRatingsView(**summary.model_dump(), reviews=reviews)
