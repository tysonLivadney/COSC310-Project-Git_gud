from fastapi import APIRouter, Depends, status
from typing import List

from dependencies import get_current_user, get_item_service
from schemas.auth import UserResponse
from schemas.item import Item, ItemCreate, ItemUpdate
from services.auth_service import require_roles
from services.items_service import ItemService


router = APIRouter(prefix="/items", tags=["items"])


@router.get("", response_model=List[Item])
def get_items(item_service: ItemService = Depends(get_item_service)):
    return item_service.list_items()


@router.post("", response_model=Item, status_code=201)
def post_item(
    payload: ItemCreate,
    item_service: ItemService = Depends(get_item_service),
    current_user: UserResponse = Depends(require_roles("owner", "manager")),
):
    return item_service.create_item(payload)


@router.get("/{item_id}", response_model=Item)
def get_item(item_id: str, item_service: ItemService = Depends(get_item_service)):
    return item_service.get_item_by_id(item_id)


@router.put("/{item_id}", response_model=Item)
def put_item(
    item_id: str,
    payload: ItemUpdate,
    item_service: ItemService = Depends(get_item_service),
    current_user: UserResponse = Depends(require_roles("owner", "manager")),
):
    return item_service.update_item(item_id, payload)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_item(
    item_id: str,
    item_service: ItemService = Depends(get_item_service),
    current_user: UserResponse = Depends(require_roles("owner", "manager")),
):
    item_service.delete_item(item_id)
    return None
