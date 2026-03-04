from fastapi import APIRouter, status
from typing import List
from schemas.item import Item, ItemCreate, ItemUpdate
from services.items_service import (
    create_item,
    delete_item,
    get_item_by_id,
    list_items,
    update_item,
)

router = APIRouter(prefix="/items", tags=["items"])

@router.get("", response_model=List[Item])
def get_items():
    return list_items()

@router.post("", response_model=Item, status_code=201)
def post_item(payload: ItemCreate):
    return create_item(payload)

@router.get("/{item_id}", response_model=Item)
def get_item(item_id: str):
    return get_item_by_id(item_id)

@router.put("/{item_id}", response_model=Item)
def put_item(item_id: str, payload: ItemUpdate):
    return update_item(item_id, payload)

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_item(item_id: str):
    delete_item(item_id)
    return None
