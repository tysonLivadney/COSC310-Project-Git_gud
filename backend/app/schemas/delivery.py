from pydantic import BaseModel, Field
from .driver import Driver
from datetime import datetime
from typing import Optional
from enum import Enum

class DeliveryStatus(str,Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    PICKED_UP = "picked_up"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class Delivery(BaseModel):
        id: str
        order_id: str
        pickup_address: Optional[str] = None
        dropoff_address: Optional[str] = None
        driver: Optional[Driver] = None
        status: DeliveryStatus = DeliveryStatus.PENDING
        estimated_arrival: Optional[datetime] = None
        created_at: datetime = Field(default_factory=datetime.now)
        updated_at: datetime = Field(default_factory=datetime.now)

Delivery.model_rebuild()