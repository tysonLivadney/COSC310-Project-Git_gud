from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional
from schemas import Delivery, Driver
from schemas.auth import UserResponse
from services import delivery_service
from services.auth_service import get_current_user

router = APIRouter(prefix="/deliveries", tags=["deliveries"])
@router.post("/", response_model=Delivery)
def create_delivery(order_id: str, pickup_address: Optional[str] = None, dropoff_address: Optional[str] = None):
    return delivery_service.create_delivery(order_id, pickup_address, dropoff_address)

@router.get("/",response_model=list[Delivery])
def get_deliveries():
    return delivery_service.get_all_deliveries()

@router.get("/{delivery_id}", response_model= Delivery)
def get_delivery(delivery_id:str):
    try:
        return delivery_service.get_delivery(delivery_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/{delivery_id}")
def delete_delivery(delivery_id: str):
    try: 
        delivery_service.delete_delivery(delivery_id)
        return {"message": f"Delivery {delivery_id} deleted"}
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.patch("/{delivery_id}/assign", response_model=Delivery)
def assign_driver(delivery_id: str, driver_id: str):
    try:
        return delivery_service.assign_driver(delivery_id, driver_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/{delivery_id}/pickup", response_model=Delivery)
def pickup_delivery(delivery_id: str, current_user: UserResponse = Depends(get_current_user)):
    try:
        return delivery_service.pickup_delivery(delivery_id, current_user.id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/{delivery_id}/transit", response_model=Delivery)
def start_transit(delivery_id: str, current_user: UserResponse = Depends(get_current_user)):
    try:
        return delivery_service.start_transit(delivery_id, current_user.id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/{delivery_id}/complete", response_model=Delivery)
def complete_delivery(delivery_id: str, current_user: UserResponse = Depends(get_current_user)):
    try:
        return delivery_service.complete_delivery(delivery_id, current_user.id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/{delivery_id}/cancel", response_model=Delivery)
def cancel_delivery(delivery_id: str):
    try:
        return delivery_service.cancel_delivery(delivery_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))