from fastapi import APIRouter, HTTPException
from schemas.notifications import Notification, NotificationType
from services import notifications_service
from schemas.delivery import Delivery

router = APIRouter(prefix="/notifications", tags=["notifications"])

@router.post("/", response_model=Notification)
def create_notifications(delivery: Delivery, notification_type: NotificationType, ):
    return notifications_service.notify(delivery,notification_type)


@router.get("/{delivery_id}", response_model=list[Notification])
def get_notifications(delivery_id:str):
    return notifications_service.get_notifications(delivery_id)


@router.patch("/{delivery_id}/{notification_id}/read", response_model=Notification)
def mark_as_read(delivery_id: str, notification_id: str):
    try:
        return notifications_service.mark_as_read(delivery_id, notification_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
@router.delete("/{delivery_id}/{notification_id}")
def delete_notification(delivery_id: str,notification_id: str):
    try: 
        notifications_service.delete_notification(delivery_id,notification_id)
        return {"message": f"Notifications for {delivery_id} deleted"}
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))