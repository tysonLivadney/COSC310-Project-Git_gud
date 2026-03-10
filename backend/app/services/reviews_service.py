import uuid
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import HTTPException
from schemas.review import Review, ReviewCreate, RatingSummary
from repositories.reviews_repo import load_all, save_all
from repositories.orders_repo import load_all as load_all_orders


def create_review(payload: ReviewCreate, user_id: str) -> Review:
    orders = load_all_orders()
    order = None
    for o in orders:
        if o.get("id") == payload.order_id:
            order = o
            break

    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.get("status") != "completed":
        raise HTTPException(status_code=400, detail="Can only review completed orders")

    if order.get("customer_id") != user_id:
        raise HTTPException(status_code=403, detail="You can only review your own orders")

    reviews = load_all()
    if any(r.get("order_id") == payload.order_id for r in reviews):
        raise HTTPException(status_code=409, detail="Review already exists for this order")

    new_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    review = Review(
        id=new_id,
        order_id=payload.order_id,
        restaurant_id=order["restaurant_id"],
        user_id=user_id,
        rating=payload.rating,
        comment=payload.comment.strip() if payload.comment else None,
        created_at=now,
    )
    reviews.append(review.dict())
    save_all(reviews)
    return review


def get_reviews_by_restaurant(restaurant_id: int, sort: Optional[str] = None) -> List[Review]:
    reviews = load_all()
    filtered = [Review(**r) for r in reviews if r.get("restaurant_id") == restaurant_id]

    if sort == "highest":
        filtered.sort(key=lambda r: r.rating, reverse=True)
    elif sort == "lowest":
        filtered.sort(key=lambda r: r.rating)
    else:
        filtered.sort(key=lambda r: r.created_at, reverse=True)

    return filtered


def get_rating_summary(restaurant_id: int) -> RatingSummary:
    reviews = load_all()
    filtered = [r for r in reviews if r.get("restaurant_id") == restaurant_id]

    total = len(filtered)
    if total == 0:
        average = 0.0
    else:
        average = round(sum(r["rating"] for r in filtered) / total, 2)

    return RatingSummary(
        restaurant_id=restaurant_id,
        average_rating=average,
        total_reviews=total,
    )
