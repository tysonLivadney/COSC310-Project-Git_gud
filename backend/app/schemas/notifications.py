from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

class NotificationType(str, Enum):
    DELIVERY_CREATED = "delivery_created"
    DELIVERY_ASSIGNED = "delivery_assigned"
    DELIVERY_PICKED_UP = "delivery_picked_up"
    DELIVERY_IN_TRANSIT = "delivery_in_transit"
    DELIVERY_COMPLETED = "delivery_completed"
    DELIVERY_CANCELLED = "delivery_cancelled"
    
class Notification(BaseModel):
    id: str
    delivery_id: str
    type: NotificationType
    message: str
    read: bool = False
    created_at: datetime = Field(default_factory=datetime.now)