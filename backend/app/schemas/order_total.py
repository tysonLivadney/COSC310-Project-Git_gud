from pydantic import BaseModel, Field
from decimal import Decimal

class OrderTotalResponse(BaseModel):
    order_id: str
    subtotal: Decimal = Field(..., max_digits = 10, decimal_places = 2)
    tax_rate: Decimal = Field(..., max_digits = 4, decimal_places = 2)
    tax: Decimal = Field(..., max_digits = 10, decimal_places = 2)
    delivery_fee: Decimal = Field(..., max_digits = 10, decimal_places = 2)
    total: Decimal = Field(..., max_digits = 10, decimal_places = 2)
    