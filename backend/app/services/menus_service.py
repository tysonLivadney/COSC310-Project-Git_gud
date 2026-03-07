import uuid
from typing import List, Dict, Any
from fastapi import HTTPException
from schemas.menu import Menu, MenuCreate, MenuUpdate
from services.menu_items_service import delete_menu_items_by_menu_id
from repositories.menus_repo import load_all, save_all
from repositories.restaurants_repo import load_all as load_restaurants

def list_menus() -> List[Dict[str, Any]]:
    return load_all()

def create_menu(payload: MenuCreate) -> Menu:
    menus = load_all()
    new_id = str(uuid.uuid4())
    if any(m.get("id") == new_id for m in menus):
        raise HTTPException(status_code=409, detail="ID collision; retry.")
    #ensure menu is attached to existing restaurant
    if not any(r["id"] == payload.restaurant_id for r in load_restaurants()):
        raise HTTPException(status_code=404, detail=f"Restaurant '{payload.restaurant_id}' not found")
    new_menu = Menu(
        id=new_id, 
        title=payload.title.strip(), 
        description=payload.description.strip(),
        restaurant_id=payload.restaurant_id.strip()
    )
    menus.append(new_menu.model_dump())
    save_all(menus)
    return new_menu

def get_menu_by_id(menu_id: str) -> Menu:
    menus = load_all()
    for m in menus:
        if m.get("id") == menu_id:
            return Menu(**m)
    raise HTTPException(status_code=404, detail=f"Menu '{menu_id}' not found")

def get_menus_by_restaurant_id(restaurant_id: str) -> List[Menu]:
    menus = load_all()
    return [Menu(**m) for m in menus if m.get("restaurant_id") == restaurant_id]

def update_menu(menu_id: str, payload: MenuUpdate) -> Menu:
    menus = load_all()
    for idx, m in enumerate(menus):
        if m.get("id") == menu_id:
            updated = Menu(
                title=payload.title.strip(),
                description=payload.description.strip(),
                restaurant_id=payload.restaurant_id.strip()
            )
            menus[idx] = updated.dict()
            save_all(menus)
            return updated
    raise HTTPException(status_code=404, detail=f"Menu '{menu_id}' not found")

def delete_menu(menu_id: str) -> None:
    delete_menu_items_by_menu_id(menu_id) #delete menu items first
    menus = load_all()
    new_menus = [m for m in menus if m.get("id") != menu_id]
    if len(new_menus) == len(menus):
        raise HTTPException(status_code=404, detail=f"Menu '{menu_id}' not found")
    save_all(new_menus)

#cascade delete menus when restaurant is deleted
def delete_menu_items_by_restaurant_id(restaurant_id: str) -> None:
    delete_menu_items_by_menu_id(restaurant_id) #delete menu items first
    menus = load_all()
    new_menus = [m for m in menus if m.get("restaurant_id") != restaurant_id]
    #no http exception since menus may not exist
    save_all(new_menus)


