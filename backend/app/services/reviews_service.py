import uuid
from datetime import datetime, timezone
from typing import List
from fastapi import HTTPException
from schemas.review import Review, ReviewCreate
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
