from pydantic import BaseModel, Field
from decimal import Decimal 
from typing import Literal

class PaymentInfo(BaseModel):
    card_number: str = Field(..., min_length=13, max_length=19)
    expiry: str = Field (...,min_length=5, max_length=5)  ## MM/YY
    cvv: str = Field (...,min_length=3, max_length=4) ## CVV 


class PaymentProcessRequest(BaseModel):
    order_id: str
    total: Decimal = Field(..., max_digits = 10, decimal_places = 2)
    payment_info: PaymentInfo


class PaymentRecord(BaseModel):
    id: str
    order_id: str
    total: Decimal = Field(..., max_digits = 10, decimal_places = 2)
    status: Literal["approved", "declined"]
    message: str


class PaymentProcessResponse(BaseModel):
    payment_id: str
    order_id: str
    status: Literal["approved", "declined"]
    message: str