from pydantic import BaseModel, Field
from typing import List

class Item(BaseModel):
    id: str
    title: str
    category: str
    tags: List[str] = Field(default_factory=list)

class ItemCreate(BaseModel):
    title: str
    category: str
    tags: List[str] = Field(default_factory=list)

class ItemUpdate(BaseModel):
    title : str
    category:str
    tags: List[str] = Field(default_factory=list)
