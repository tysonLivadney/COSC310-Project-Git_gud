from fastapi import APIRouter, status, Query
from typing import List
from schemas.menu_item import MenuItem, MenuItemCreate, MenuItemUpdate
from services.menu_items_service import list_menu_items, create_menu_item, delete_menu_item, update_menu_item, get_menu_item_by_id, search_menu_items

router = APIRouter(prefix="/menu-items", tags=["menu-items"])

@router.get("", response_model=List[MenuItem])
def get_menu_items():
    return list_menu_items()

@router.post("", response_model=MenuItem, status_code=201)
def post_menu_item(payload: MenuItemCreate):
    return create_menu_item(payload)

@router.get("/search", response_model = List[MenuItem])
def get_menu_items_filtered(
    menu_id: str=None,
    name: str = None, cuisine: str = None,
    max_price: int = None, 
    limit: int = Query(10, ge=1, le=20, description="Number of items to return"),
    offset: int = Query(0, ge=0, description="Number of items to skip")):
    return search_menu_items(menu_id=menu_id, name=name, max_price=max_price, limit=limit, offset=offset)


@router.get("/{menu_item_id}", response_model=MenuItem)
def get_menu_item(menu_item_id: str):
    return get_menu_item_by_id(menu_item_id)

@router.put("/{menu_item_id}", response_model=MenuItem)
def put_menu_item(menu_item_id: str, payload: MenuItemUpdate):
    return update_menu_item(menu_item_id, payload)

@router.delete("/{menu_item_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_menu_item(menu_item_id: str):
    delete_menu_item(menu_item_id)
    return None