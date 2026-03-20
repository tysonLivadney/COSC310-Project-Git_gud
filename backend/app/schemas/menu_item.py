from pydantic import BaseModel, Field
from typing import List
from decimal import Decimal

class MenuItemCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=50)
    description: str = Field(..., max_length=300)
    price: float = Field(..., ge = 0, lt = 10000)
    in_stock: bool
    menu_id: str

class MenuItem(MenuItemCreate):
    id: str

class MenuItemUpdate(BaseModel):
    name: str = Field(None, min_length=3, max_length=50)
    description: str= Field(None, max_length=300)
    price: Decimal = Field(None, ge = 0, decimal_places = 2, max_digits = 6)
    in_stock: bool = None