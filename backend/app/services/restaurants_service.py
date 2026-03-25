import uuid
from typing import List, Optional
from fastapi import HTTPException
from schemas.restaurant import Restaurant, RestaurantCreate, RestaurantUpdate
from repositories.restaurants_repo import load_all, save_all

def list_restaurants() -> List[Restaurant]:
    return [Restaurant(**r) for r in load_all()]

def create_restaurant(payload: RestaurantCreate) -> Restaurant:
    restaurants = load_all()
    new_id = str(uuid.uuid4())
    if any(r.get("id") == new_id for r in restaurants):
        raise HTTPException(status_code=409, detail="ID collision; retry.")
    new_restaurant = Restaurant(
        id=new_id,
        name=payload.name.strip(),
        address=payload.address.strip(), 
        description=payload.description.strip(),
        phone=payload.phone.strip(),
        rating=payload.rating, 
        tags=payload.tags,
        estimated_delivery_time=payload.estimated_delivery_time
        )
    restaurants.append(new_restaurant.model_dump())
    save_all(restaurants)
    return new_restaurant

def get_restaurant_by_id(restaurant_id: str) -> Restaurant:
    restaurants = load_all()
    for r in restaurants:
        if r.get("id") == restaurant_id:
            return Restaurant(**r)
    raise HTTPException(status_code=404, detail=f"Restaurant '{restaurant_id}' not found")

def search_restaurants(
    name: Optional[str] = None,
    cuisine: Optional[str] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
) -> List[Restaurant]:
    restaurants = load_all()
    if cuisine:
        restaurants = [r for r in restaurants if cuisine.lower() in[t.lower() for t in r["tags"]]]
    if name:
        restaurants = [r for r in restaurants if name.lower() in r["name"].lower()]
    start = 0 if offset is None else offset
    end = None if limit is None else start + limit
    return [Restaurant(**r) for r in restaurants[start:end]]

def update_restaurant(restaurant_id: str, payload: RestaurantUpdate) -> Restaurant:
    restaurants = load_all()
    for idx, r in enumerate(restaurants):
        if r.get("id") == restaurant_id:
            current_tags = r.get("tags")
            normalized_tags = current_tags if isinstance(current_tags, list) else []
            final_tags: List[str] = payload.tags if payload.tags is not None else normalized_tags
            updated = Restaurant(
                id=restaurant_id,
                name=payload.name.strip() if payload.name is not None else str(r.get("name")),
                address=payload.address.strip() if payload.address is not None else str(r.get("address")),
                description=payload.description.strip() if payload.description is not None else str(r.get("description")),
                phone=payload.phone.strip() if payload.phone is not None else str(r.get("phone")),
                rating=payload.rating if payload.rating is not None else r.get("rating"),
                tags=final_tags,
                estimated_delivery_time=(
                    payload.estimated_delivery_time
                    if payload.estimated_delivery_time is not None
                    else r.get("estimated_delivery_time")
                ),
            )
            restaurants[idx] = updated.model_dump()
            save_all(restaurants)
            return updated
    raise HTTPException(status_code=404, detail=f"Restaurant '{restaurant_id}' not found")

def delete_restaurant(restaurant_id: str) -> None:
    restaurants = load_all()
    new_restaurants = [r for r in restaurants if r.get("id") != restaurant_id]
    if len(new_restaurants) == len(restaurants):
        raise HTTPException(status_code=404, detail=f"Restaurant '{restaurant_id}' not found")
    save_all(new_restaurants)

    