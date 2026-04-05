import uuid
from typing import List, Optional
from fastapi import HTTPException
from schemas.restaurant import Restaurant, RestaurantCreate, RestaurantUpdate
from repositories.restaurants_repo import load_all, save_all
from datetime import datetime

def list_restaurants() -> List[Restaurant]:
    return [Restaurant(**r) for r in load_all()]

def create_restaurant(payload: RestaurantCreate, owner_id: str) -> Restaurant:
    restaurants = load_all()
    new_id = str(uuid.uuid4())
    if any(r.get("id") == new_id for r in restaurants):
        raise HTTPException(status_code=409, detail="ID collision; retry.")
    new_restaurant = Restaurant(
        id=new_id,
        owner_id=owner_id,
        name=payload.name.strip(),
        address=payload.address.strip(),
        description=payload.description.strip(),
        phone=payload.phone.strip(),
        rating=payload.rating, 
        tags=payload.tags,
        opening_hours=payload.opening_hours,
        closing_hours=payload.closing_hours,
        max_prep_time_minutes=payload.max_prep_time_minutes 
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

def update_restaurant(restaurant_id: str, payload: RestaurantUpdate, owner_id: str) -> Restaurant:
    restaurants = load_all()
    for idx, r in enumerate(restaurants):
        if r.get("id") == restaurant_id:
            current_tags = r.get("tags")
            normalized_tags = current_tags if isinstance(current_tags, list) else []
            final_tags: List[str] = payload.tags if payload.tags is not None else normalized_tags
            updated = Restaurant(
                id=restaurant_id,
                owner_id=owner_id,
                name=payload.name.strip() if payload.name is not None else str(r.get("name")),
                address=payload.address.strip() if payload.address is not None else str(r.get("address")),
                description=payload.description.strip() if payload.description is not None else str(r.get("description")),
                phone=payload.phone.strip() if payload.phone is not None else str(r.get("phone")),
                rating=payload.rating if payload.rating is not None else r.get("rating"),
                tags=final_tags,
                opening_hours=payload.opening_hours if payload.opening_hours is not None else r.get("opening_hours"),
                closing_hours=payload.closing_hours if payload.closing_hours is not None else r.get("closing_hours"),
                max_prep_time_minutes=payload.max_prep_time_minutes if payload.max_prep_time_minutes is not None else r.get("max_prep_time_minutes")
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

def _get_current_day_index() -> int:
    # Monday=0 -> Sunday=6
    return datetime.now().weekday()

def _is_open(self) -> bool:
    day = _get_current_day_index()
    open_time = self.opening_hours[day]
    close_time = self.closing_hours[day]
    if open_time in ("", "closed") or close_time in ("", "closed"):
        return False
    now = datetime.now().strftime("%H:%M")
    return open_time <= now < close_time

def _finishes_before_close(self) -> bool:
    day = _get_current_day_index()
    close_time = self.closing_hours[day]
    if close_time in ("", "closed"):
        return False
    now = datetime.now().strftime("%H:%M")
    return now < close_time

def can_accept_order(self) -> bool:
    return self._is_open() and self._finishes_before_close()

    
        