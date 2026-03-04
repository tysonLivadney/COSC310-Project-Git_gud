from fastapi import APIRouter, Depends, status
from typing import List
from schemas.item import Item, ItemCreate, ItemUpdate
from schemas.auth import UserResponse
from services.auth_service import require_roles
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
def post_item(
    payload: ItemCreate,
    current_user: UserResponse = Depends(require_roles("owner", "manager")),
):
    return create_item(payload)

@router.get("/{item_id}", response_model=Item)
def get_item(item_id: str):
    return get_item_by_id(item_id)

@router.put("/{item_id}", response_model=Item)
def put_item(
    item_id: str,
    payload: ItemUpdate,
    current_user: UserResponse = Depends(require_roles("owner", "manager")),
):
    return update_item(item_id, payload)

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_item(
    item_id: str,
    current_user: UserResponse = Depends(require_roles("owner", "manager")),
):
    delete_item(item_id)
    return None
