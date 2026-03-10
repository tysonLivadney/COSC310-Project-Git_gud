from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class OrderStatus(str, Enum):
    DRAFT = "draft"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class OrderItem(BaseModel):
    food_item: str
    quantity: int = Field(..., ge=1)
    unit_price: float = Field(..., gt=0)


class OrderCreate(BaseModel):
    restaurant_id: int
    customer_id: str
    items: List[OrderItem] = Field(..., min_length=1)


class OrderUpdate(BaseModel):
    items: List[OrderItem] = Field(..., min_length=1)


class Order(BaseModel):
    id: str
    restaurant_id: int
    customer_id: str
    items: List[OrderItem]
    status: OrderStatus = OrderStatus.DRAFT
    created_at: str
    confirmed_at: Optional[str] = None
