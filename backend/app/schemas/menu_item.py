from pydantic import BaseModel, Field
from typing import Optional

class MenuItemCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=50)
    description: str = Field(..., max_length=300)
    price: float = Field(..., ge = 0, lt = 10000)
    in_stock: bool
    menu_id: str 

class MenuItem(MenuItemCreate):
    id: str

class MenuItemUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=3, max_length=50)
    description: Optional[str] = Field(default=None, max_length=300)
    price: Optional[float] = Field(default=None, ge=0, lt=10000)
    in_stock: Optional[bool] = None
