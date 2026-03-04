import uuid
from typing import List, Dict, Any
from fastapi import HTTPException
from schemas.menu_item import MenuItem, MenuItemCreate, MenuItemUpdate
from schemas.menu import Menu
from repositories.menu_items_repo import load_all, save_all
from repositories.menus_repo import load_all as load_menus
from repositories.restaurants_repo import load_all as load_restaurants

def list_menu_items() -> List[Dict[str, Any]]:
    return load_all()

def create_menu_item(payload: MenuItemCreate) -> MenuItem:
    menu_items = load_all()
    new_id = str(uuid.uuid4())
    if any(m.get("id") == new_id for m in menu_items):
        raise HTTPException(status_code=409, detail="ID collision; retry.")
    #ensure menu item is attached to existing menu
    if not any(r["id"] == payload.menu_id for r in load_menus()):
        raise HTTPException(status_code=404, detail=f"Menu '{payload.menu_id}' not found")
    new_menu_item = MenuItem(
        id=new_id, 
        title=payload.title.strip(), 
        description=payload.description.strip(),
        price=payload.price,
        in_stock=payload.in_stock,
        menu_id=payload.menu_id.strip()
    )
    menu_items.append(new_menu_item.dict())
    save_all(menu_items)
    return new_menu_item

def get_menu_item_by_id(menu_item_id: str) -> MenuItem:
    menu_items = load_all()
    for m in menu_items:
        if m.get("id") == menu_item_id:
            return MenuItem(**m)
    raise HTTPException(status_code=404, detail=f"Menu Item '{menu_item_id}' not found")

def get_menu_items_by_menu_id(menu_id: str) -> List[MenuItem]:
    menu_items = load_all()
    return [MenuItem(**m) for m in menu_items if m.get("menu_id") == menu_id]

def get_menu_items_by_restaurant_id(restaurant_id: str) -> List[MenuItem]:
    menus = load_menus()
    menu_items = load_all()
    menu_ids = [Menu(**m) for m in menus if m.get("restaurant_id") == restaurant_id]
    return [MenuItem(**m) for m in menu_items if m.get("menu_id") in menu_ids]


def update_menu_item(menu_item_id: str, payload: MenuItemUpdate) -> MenuItem:
    menu_items = load_all()
    for idx, m in enumerate(menu_items):
        if m.get("id") == menu_item_id:
            updated = MenuItem(
                title=payload.title.strip(),
                description=payload.description.strip(), 
                price=payload.price,
                in_stock=payload.in_stock,
                menu_id=m.get("menu_id")
            )
            menu_items[idx] = updated.dict()
            save_all(menu_items)
            return updated
    raise HTTPException(status_code=404, detail=f"Menu Item '{menu_item_id}' not found")

def delete_menu_item(menu_item_id: str) -> None:
    menu_items = load_all()
    new_menu_items = [m for m in menu_items if m.get("id") != menu_item_id]
    if len(new_menu_items) == len(menu_items):
        raise HTTPException(status_code=404, detail=f"Menu Item '{menu_item_id}' not found")
    save_all(new_menu_items)

#cascade delete items when menu is deleted
def delete_menu_items_by_menu_id(menu_id: str) -> None:
    menu_items = load_all()
    new_menu_items = [m for m in menu_items if m.get("menu_id") != menu_id]
    if len(new_menu_items) == len(menu_items):
        raise HTTPException(status_code=404, detail=f"Menu Items for Menu '{menu_id}' not found")
    save_all(new_menu_items)


