from schemas.notifications import Notification, NotificationType
from schemas.delivery import Delivery
from repositories.notifications_repo import save_all, load_all
from uuid import uuid4

def _load_notifications() -> dict[int, list[dict]]:
    notis = load_all()
    result: dict[str, list[dict]] = {}
    for n in notis:
        delivery_id = n["delivery_id"]
        result.setdefault(delivery_id, []).append(n)
    return result



def notify(delivery: Delivery, notification_type: NotificationType) -> Notification:
    message = _build_message(delivery,notification_type)
    notification = Notification(
        id = str(uuid4()),
        delivery_id=delivery.id,
        type=notification_type,
        message=message
    )
    
    all_notifications = _load_notifications()
    all_notifications.setdefault(delivery.id, []).append(notification.model_dump(mode="json"))
    
    temp = [n for group in all_notifications.values() for n in group]
    save_all(temp)
    
    return notification
 
 
def get_notifications(delivery_id: str) -> list[Notification]:
    all_notifications = _load_notifications()
    return [Notification(**n) for n in all_notifications.get(delivery_id,[])]

def mark_as_read(delivery_id:str, notification_id:str) -> Notification:
    all_notifications = _load_notifications()
    notifications = all_notifications.get(delivery_id)

    if not notifications:
        raise KeyError(f"No notifications found for delivery {delivery_id}")

    for n in notifications:
        if n["id"] == notification_id:
            n["read"] = True
            temp = [n for group in all_notifications.values() for n in group]
            save_all(temp)
            return Notification(**n)
    raise KeyError(f"Notification {notification_id} not found")

def delete_notification(delivery_id: str, notification_id: str) -> Notification:
        all_notifications = _load_notifications()
        notifications = all_notifications.get(delivery_id)
        if not notifications:
            raise KeyError(f"No notifications found for delivery: {delivery_id}")
        for i, n in enumerate(notifications):
            if n["id"] == notification_id:
                removed = notifications.pop(i)
                if not notifications:
                    del all_notifications[delivery_id]
                temp = [n for group in all_notifications.values() for n in group]
                save_all(temp)
                return Notification(**removed)
        raise KeyError(f"Notification {notification_id} not found")

notifications:dict[int,list[Notification]] = {}
_next_id = 1

def notify(delivery: Delivery, notification_type: NotificationType) -> Notification:
    global _next_id
    message = _build_message(delivery,notification_type)
    notification = Notification(
        id = _next_id,
        delivery_id=delivery.id,
        type=notification_type,
        message=message,
    )
    if delivery.id not in notifications:
        notifications[delivery.id].append(notification)
        _next_id += 1
        return notification
    
def get_notifications(delivery_id: int) -> list[Notification]:
    return notifications.get(delivery_id,[])

def mark_as_read(delivery_id:int, notification_id:int) -> Notification:
    delivery_notifications = notifications.get(delivery_id, [])
    for n in delivery_notifications:
        if n.id == notification_id:
            n.read = True
            return n
        raise KeyError(f"Notification {notification_id} not found")


    
    
def _build_message(delivery: Delivery, notification_type: NotificationType) -> str:
    messages = {
        NotificationType.DELIVERY_CREATED: f"Delivery {delivery.id} has been created for order {delivery.order_id}",
        NotificationType.DELIVERY_ASSIGNED: f"Delivery {delivery.id} has been assigned to driver {delivery.driver.name if delivery.driver else 'unknown'}",
        NotificationType.DELIVERY_PICKED_UP: f"Delivery {delivery.id} has been picked up",
        NotificationType.DELIVERY_IN_TRANSIT: f"Delivery {delivery.id} is on the way",
        NotificationType.DELIVERY_COMPLETED: f"Delivery {delivery.id} has been delivered",
        NotificationType.DELIVERY_CANCELLED: f"Delivery {delivery.id} has been cancelled",
    }
    return messages[notification_type]