from fastapi import APIRouter, HTTPException, status
from schemas import Delivery, Driver
from . import service

router = APIRouter(prefix="/deliveries", tags=["deliveries"])
@router.post("/", response_model=Delivery)
def create_delivery(order_id: int, pickup_address: str, dropoff_address: str):
    return service.create_delivery(order_id, pickup_address, dropoff_address)

@router.get("/",response_model=list[Delivery])
def get_deliverys():
    return list(service.deliveries.values())


@router.patch("/{delivery_id}/assign", response_model=Delivery)
def assign_driver(delivery_id: int, driver:Driver):
    try:
        return service.assign_driver(delivery_id,driver)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.patch("/{delivery_id}/pickup", response_model=Delivery)
def pickup_delivery(delivery_id: int):
    try:
        return service.pickup_delivery(delivery_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.patch("/{delivery_id}/transit", response_model=Delivery)
def start_tranist(delivery_id: int):
    try:
        return service.start_tranist(delivery_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.patch("/{delivery_id}/complete", response_model=Delivery)
def complete_delivery(delivery_id: int):
    try:
        return service.complete_delivery(delivery_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.patch("/{delivery_id}/cancel", response_model=Delivery)
def cancel_delivery(delivery_id: int):
    try:
        return service.cancel_delivery(delivery_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
