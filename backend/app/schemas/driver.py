from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum

class DriverStatus(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    BUSY = "busy"

class Driver(BaseModel):
    id: int
    name: str
    phone: str
    status: DriverStatus = DriverStatus.OFFLINE
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.now)