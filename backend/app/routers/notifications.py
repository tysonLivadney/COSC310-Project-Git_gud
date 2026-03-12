from fastapi import APIRouter, HTTPException
from schemas.notifications import Notification
from services import notifications_service

router = APIRouter(prefix="/notifications", tags=["notifications"])

@router.get("/{delivery_id}", response_model=list[Notification])
def get_notifications(delivery_id:int):
    return notifications_service.get_notifications(delivery_id)


@router.patch("/{delivery_id}/{notification_id}/read", response_model=Notification)
def mark_as_read(delivery_id: int, notification_id: int):
    try:
        return notifications_service.mark_as_read(delivery_id, notification_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
