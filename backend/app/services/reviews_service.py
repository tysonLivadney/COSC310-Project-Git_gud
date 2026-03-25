import uuid
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import HTTPException
from schemas.review import Review, ReviewCreate, RatingSummary, RestaurantRatingsView
from repositories.reviews_repo import load_all, save_all
from repositories.orders_repo import load_all as load_all_orders


SORT_OPTIONS = {
    "highest": lambda r: r.rating,
    "lowest": lambda r: r.rating,
}

SORT_REVERSE = {
    "highest": True,
    "lowest": False,
}


def _find_order(order_id: str) -> dict:
    for o in load_all_orders():
        if o.get("id") == order_id:
            return o
    raise HTTPException(status_code=404, detail="Order not found")


def _validate_review_eligibility(order: dict, user_id: str) -> None:
    if order.get("status") != "completed":
        raise HTTPException(status_code=400, detail="Can only review completed orders")
    if order.get("customer_id") != user_id:
        raise HTTPException(status_code=403, detail="You can only review your own orders")


def _check_duplicate_review(order_id: str) -> None:
    if any(r.get("order_id") == order_id for r in load_all()):
        raise HTTPException(status_code=409, detail="Review already exists for this order")


def create_review(payload: ReviewCreate, user_id: str) -> Review:
    order = _find_order(payload.order_id)
    _validate_review_eligibility(order, user_id)
    _check_duplicate_review(payload.order_id)

    new_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    review = Review(
        id=new_id,
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
    if sort and sort in SORT_OPTIONS:
        key_fn = SORT_OPTIONS[sort]
        reverse = SORT_REVERSE[sort]
    else:
        key_fn = lambda r: r.created_at
        reverse = True
    reviews.sort(key=key_fn, reverse=reverse)
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
    return RestaurantRatingsView(
        restaurant_id=restaurant_id,
        average_rating=summary.average_rating,
        total_reviews=summary.total_reviews,
        reviews=reviews,
    )
