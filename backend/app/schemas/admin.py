from pydantic import BaseModel
from typing import List, Optional


class RestaurantRevenue(BaseModel):
    restaurant_id: str
    total_revenue: float
    order_count: int


class AdminReport(BaseModel):
    total_revenue: float
    revenue_per_restaurant: List[RestaurantRevenue]
    average_delivery_time: Optional[float] = None
    highest_rated_restaurants: List[int] = []
