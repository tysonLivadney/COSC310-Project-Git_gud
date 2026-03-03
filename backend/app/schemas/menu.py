from pydantic import baseModel, Field
from typing import List, Optional

class MenuCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=50)
    description: str = Field(..., max_length=300)
    items: List[str] = Field(default=[], max_items=100)
    restaurant_id: str = Field(..., min_length=1) #link to restaurant

class Menu(MenuCreate):
    id: str

class MenuUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=50)
    description: Optional[str] = Field(None, max_length=300)
    items: Optional[List[str]] = Field(default=[], max_items=100)
    #restaurant shouldn't have to be updated

