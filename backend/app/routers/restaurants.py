# from fastapi import APIRouter, status
# from typing import List
# from schemas.restaurant import Restaurant, RestaurantCreate, RestaurantUpdate
# from services.restaurants_service import list_restaurants, create_restaurant, delete_restaurant, update_restaurant, get_restaurant_id

# router = APIRouter(prefix="/restaurants", tags=["restaurants"])

# @router.get("", response_model=List[Restaurant])
# def get_restaurants():
#     return list_restaurants()

# RETURNING TO THIS ONCE I DO SERVICES