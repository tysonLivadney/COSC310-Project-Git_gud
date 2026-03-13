from fastapi import APIRouter, status
from typing import List
from schemas.menu import Menu, MenuCreate, MenuUpdate
from schemas.menu_item import MenuItem
from services.menus_service import list_menus, create_menu, delete_menu, update_menu, get_menu_by_id
from services.menu_items_service import get_menu_items_by_menu_id, delete_menu_items_by_menu_id

router = APIRouter(prefix="/menus", tags=["menus"])

@router.get("", response_model=List[Menu])
def get_menus():
    return list_menus()

@router.post("", response_model=Menu, status_code=201)
def post_menu(payload: MenuCreate):
    return create_menu(payload)

@router.get("/{menu_id}", response_model=Menu)
def get_menu(menu_id: str):
    return get_menu_by_id(menu_id)

@router.get("/{menu_id}/items", response_model=List[MenuItem])
def get_menu_items_by_menu(menu_id: str):
    return get_menu_items_by_menu_id(menu_id)

@router.put("/{menu_id}", response_model=Menu)
def put_menu(menu_id: str, payload: MenuUpdate):
    return update_menu(menu_id, payload)

@router.delete("/{menu_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_menu(menu_id: str):
    delete_menu_items_by_menu_id(menu_id) #delete menu items first
    delete_menu(menu_id)
    return None


