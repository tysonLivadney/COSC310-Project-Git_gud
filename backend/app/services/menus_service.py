import uuid
from typing import List, Dict, Any
from fastapi import HTTPException
from schemas.menu import Menu, MenuCreate, MenuUpdate
from repositories.items_repo import load_all, save_all

def list_menus() -> List[Dict[str, Any]]:
    return load_all()

def create_menu(payload: Dict[str, Any]) -> Menu:
    menus = load_all()
    new_id = str(uuid.uuid4())
    if any(m.get("id") == new_id for m in menus):
        raise HTTPException(status_code=409, detail="ID collision; retry.")
    new_menu = Menu(id=new_id, title=payload["title"].strip(), items=payload["items"])
    menus.append(new_menu.dict())
    save_all(menus)
    return new_menu.dict()

def get_menu_by_id(menu_id: str) -> Menu:
    menus = load_all()
    for m in menus:
        if m.get("id") == menu_id:
            return Menu(**m)
    raise HTTPException(status_code=404, detail=f"Menu '{menu_id}' not found")

def get_menus_by_restaurant_id(restaurant_id: str) -> List[Menu]:
    menus = load_all()
    return [Menu(**m) for m in menus if m.get("restaurant_id") == restaurant_id]

def update_menu(menu_id: str, payload: Dict[str, Any]) -> Menu:
    menus = load_all()
    for idx, m in enumerate(menus):
        if m.get("id") == menu_id:
            updated = Menu(
                id=menu_id,
                title=payload["title"].strip(),
                items=payload["items"],
            )
            menus[idx] = updated.dict()
            save_all(menus)
            return updated
    raise HTTPException(status_code=404, detail=f"Menu '{menu_id}' not found")

def delete_menu(menu_id: str) -> None:
    menus = load_all()
    new_menus = [m for m in menus if m.get("id") != menu_id]
    if len(new_menus) == len(menus):
        raise HTTPException(status_code=404, detail=f"Menu '{menu_id}' not found")
    save_all(new_menus)


