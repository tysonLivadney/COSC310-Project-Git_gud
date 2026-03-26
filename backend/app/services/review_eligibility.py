from fastapi import HTTPException
from repositories.orders_repo import load_all as load_all_orders
from repositories.reviews_repo import load_all as load_all_reviews


def find_order(order_id: str) -> dict:
    for o in load_all_orders():
        if o.get("id") == order_id:
            return o
    raise HTTPException(status_code=404, detail="Order not found")


def validate_review_eligibility(order: dict, user_id: str) -> None:
    if order.get("status") != "completed":
        raise HTTPException(status_code=400, detail="Can only review completed orders")
    if order.get("customer_id") != user_id:
        raise HTTPException(status_code=403, detail="You can only review your own orders")


def check_duplicate_review(order_id: str) -> None:
    if any(r.get("order_id") == order_id for r in load_all_reviews()):
        raise HTTPException(status_code=409, detail="Review already exists for this order")
