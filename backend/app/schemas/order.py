from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from enum import Enum
from schemas.payment import PaymentInfo

class OrderConfirmRequest(BaseModel):
    payment_info: PaymentInfo

class OrderStatus(str, Enum):
    DRAFT = "draft"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class OrderItem(BaseModel):
    food_item: str
    quantity: int = Field(..., ge=1)
    unit_price: float = Field(..., gt=0)


class OrderCreate(BaseModel):
    restaurant_id: str
    customer_id: str
    items: List[OrderItem] = Field(..., min_length=1)
    delivery_address: Optional[str] = None
    @field_validator("restaurant_id", mode="before")
    @classmethod
    def coerce_restaurant_id_to_str(cls, v):
        return str(v)
    


class OrderUpdate(BaseModel):
    items: List[OrderItem] = Field(..., min_length=1)


class Order(BaseModel):
    id: str
    restaurant_id: str
    customer_id: str
    items: List[OrderItem]
    status: OrderStatus = OrderStatus.DRAFT
    created_at: str
    confirmed_at: Optional[str] = None
    cancelled_at: Optional[str] = None
    refunded_at: Optional[str] = None
    refund_amount: Optional[str] = None
    @field_validator("restaurant_id", mode="before")
    @classmethod
    def coerce_restaurant_id_to_str(cls, v):
        return str(v)
    delivery_address: Optional[str] = None

