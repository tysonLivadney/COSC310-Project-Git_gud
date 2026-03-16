from pydantic import BaseModel, Field
from typing import List

class MenuCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=50)
    description: str = Field(..., max_length=300)
    restaurant_id: str #link to restaurant

class Menu(MenuCreate):
    id: str

class MenuUpdate(BaseModel):
    name: str = Field(None, min_length=3, max_length=50)
    description: str= Field(None, max_length=300)
    #restaurant shouldn't have to be updated