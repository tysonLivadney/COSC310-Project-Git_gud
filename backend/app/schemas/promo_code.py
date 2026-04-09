from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class DiscountType(str, Enum):
    PERCENTAGE = "percentage"
    FLAT = "flat"


class PromoCodeCreate(BaseModel):
    code: str
    discount_type: DiscountType
    discount_value: float = Field(..., gt=0)
    expiry_date: Optional[str] = None
    max_uses: Optional[int] = None
    min_order_amount: Optional[float] = None


class PromoCode(BaseModel):
    id: str
    code: str
    discount_type: DiscountType
    discount_value: float
    expiry_date: Optional[str] = None
    max_uses: Optional[int] = None
    min_order_amount: Optional[float] = None
    usage_count: int = 0
    active: bool = True
    created_at: str


class PromoCodeValidateRequest(BaseModel):
    code: str
    order_subtotal: float
