from pydantic import BaseModel, Field
from typing import Literal


class PaymentInfo(BaseModel):
    card_number: str = Field(..., min_length=12)
    expiry: str
    cvv: str


class PaymentProcessRequest(BaseModel):
    order_id: str
    total: float
    payment_info: PaymentInfo


class PaymentRecord(BaseModel):
    id: str
    order_id: str
    total: float
    status: Literal["approved", "declined"]
    message: str


class PaymentProcessResponse(BaseModel):
    payment_id: str
    order_id: str
    status: Literal["approved", "declined"]
    message: str