import json
import os
from datetime import datetime
from typing import Optional
from schemas import Delivery, DeliveryStatus, Driver

SAVE_FILE = "deliveries.json"

class DeliveryRepo:
    def __init__(self, filepath:str = SAVE_FILE):
        self.filepath= filepath
        self.deliveries:dict[int, Delivery] = {}
        self._load()
  
    def save(self, delivery: Delivery) -> None:
        self.deliveries[delivery.id] = delivery
        self._persist()

    def get(self, delivery_id: int) -> Optional[Delivery]:
        return self.deliveries.get(delivery_id)
    
    def get_all(self) -> list[Delivery]:
        return list(self.deliveries.values())

    def delete(self, delivery_id: int) -> None:
        if delivery_id not in self.deliveries:
            raise KeyError(f"Delivery {delivery_id} not found")
        del self.deliveries[delivery_id]
        self._persist()

    def _persist(self) -> None:
        with open(self.filepath, "w") as f:
            json.dump(
                {k: self._serialize(v) for k, v in self.deliveries.items()},
                f,
                indent=2
            )
 
    def _load(self) -> None:
        if not os.path.exists(self.filepath):
            return
        with open(self.filepath, "r") as f:
            data = json.load(f)
            self.deliveries = {
                int(k): self._deserialize(v) for k, v in data.items()
            }

 

    def _serialize(self, delivery: Delivery) -> dict:
        data = delivery.model_dump()
        data["status"] = delivery.status.value
        data["created_at"] = delivery.created_at.isoformat()
        data["updated_at"] = delivery.updated_at.isoformat()
        if delivery.estimated_arrival:
            data["estimated_arrival"] = delivery.estimated_arrival.isoformat()
        if delivery.driver:
            data["driver"]["status"] = delivery.driver.status.value
            data["driver"]["created_at"] = delivery.driver.created_at.isoformat()
        return data

    def _deserialize(self, data: dict) -> Delivery:
        data["status"] = DeliveryStatus(data["status"])
        data["created_at"] = datetime.fromisoformat(data["created_at"])
        data["updated_at"] = datetime.fromisoformat(data["updated_at"])
        if data.get("estimated_arrival"):
            data["estimated_arrival"] = datetime.fromisoformat(data["estimated_arrival"])
        if data.get("driver"):
            data["driver"]["created_at"] = datetime.fromisoformat(data["driver"]["created_at"])
            data["driver"] = Driver(**data["driver"])
        return Delivery(**data)