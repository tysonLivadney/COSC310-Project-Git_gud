from fastapi import APIRouter, status
from typing import List
from schemas.restaurant import Restaurant, RestaurantCreate, RestaurantUpdate
from services.restaurants_service import list_restaurants, create_restaurant, delete_restaurant, update_restaurant, get_restaurant_by_id
from services.menus_service import get_menus_by_restaurant_id
from schemas.menu import Menu

router = APIRouter(prefix="/restaurants", tags=["restaurants"])

@router.get("", response_model=List[Restaurant])
def get_restaurants():
    return list_restaurants()

@router.post("", response_model=Restaurant, status_code=201)
def post_restaurant(payload: RestaurantCreate):
    return create_restaurant(payload)

@router.get("/{restaurant_id}", response_model=Restaurant)
def get_restaurant(restaurant_id: str):
    return get_restaurant_by_id(restaurant_id)

@router.get("/{restaurant_id}/menus", response_model=List[Menu])
def get_menus_by_restaurant(restaurant_id: str):
    return get_menus_by_restaurant_id(restaurant_id)

@router.put("/{restaurant_id}", response_model=Restaurant)
def put_restaurant(restaurant_id: str, payload: RestaurantUpdate):
    return update_restaurant(restaurant_id, payload)

@router.delete("/{restaurant_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_restaurant(restaurant_id: str):
    delete_restaurant(restaurant_id)
    return None
