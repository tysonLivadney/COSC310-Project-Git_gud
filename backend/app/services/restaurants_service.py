import uuid
from typing import List, Dict, Any
from fastapi import HTTPException
from schemas.restaurant import Restaurant, RestaurantCreate, RestaurantUpdate
from repositories.restaurants_repo import load_all, save_all

def list_restaurants() -> List[Restaurant]:
    return [Restaurant(**r) for r in load_all()]

def create_restaurant(payload: RestaurantCreate) -> Restaurant:
    restaurants = load_all()
    new_id = str(uuid.uuid4())
    if any(r.get("id") == new_id for r in restaurants): #unlikely safety check
        raise HTTPException(status_code=409, detail="ID collision; retry.")
    #strip() removes whitespace from strings
    new_restaurant = Restaurant(id=new_id, name=payload.name.strip(), address=payload.address.strip(), description=payload.description.strip(), phone=payload.phone.strip(), tags=payload.tags)
    restaurants.append(new_restaurant.dict())
    save_all(restaurants)
    return new_restaurant

def get_restaurant_id(restaurant_id: str) -> Restaurant:
    restaurants = load_all()
    for r in restaurants:
        if r.get("id") == restaurant_id:
            return Restaurant(**r)
    raise HTTPException(status_code=404, detail=f"Restaurant '{restaurant_id}' not found")

def update_restaurant(restaurant_id: str, payload: RestaurantUpdate) -> Restaurant:
    restaurants = load_all()
    for idx, r in enumerate(restaurants):
        if r.get("id") == restaurant_id:
            updated = Restaurant(
                id=restaurant_id,
                name=payload.name.strip(),
                address=payload.address.strip(),
                description=payload.description.strip(),
                phone=payload.phone.strip(),
                tags=payload.tags,
            )
            restaurants[idx] = updated.dict()
            save_all(restaurants)
            return updated
    raise HTTPException(status_code=404, detail=f"Restaurant '{restaurant_id}' not found")

def delete_restaurant(restaurant_id: str) -> None:
    restaurants = load_all()
    new_restaurants = [r for r in restaurants if r.get("id") != restaurant_id]
    if len(new_restaurants) == len(restaurants):
        raise HTTPException(status_code=404, detail=f"Restaurant '{restaurant_id}' not found")
    save_all(new_restaurants)
    