from pydantic import BaseModel, Field
from typing import List

class MenuCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=50)
    description: str = Field(..., max_length=300)
    restaurant_id: str = Field(..., min_length=1) #link to restaurant

class Menu(MenuCreate):
    id: str

class MenuUpdate(BaseModel):
    title: str = Field(None, min_length=3, max_length=50)
    description: str= Field(None, max_length=300)
    #restaurant shouldn't have to be updated

