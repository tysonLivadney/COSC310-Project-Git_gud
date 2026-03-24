import pytest
from uuid import uuid4
from schemas.delivery import Delivery, DeliveryStatus
from schemas.notifications import Notification, NotificationType
from services import notifications_service

def test_notify_returns_notification(sample_delivery):
    result = notifications_service.notify(sample_delivery, NotificationType.DELIVERY_CREATED)
    assert result.delivery_id == sample_delivery.id
    assert result.type == NotificationType.DELIVERY_CREATED
    assert result.read == False

def test_notify_generates_unique_ids(sample_delivery):
    n1 = notifications_service.notify(sample_delivery, NotificationType.DELIVERY_CREATED)
    n2 = notifications_service.notify(sample_delivery, NotificationType.DELIVERY_ASSIGNED)
    assert n1.id != n2.id

def test_notify_builds_correct_message(sample_delivery):
    result = notifications_service.notify(sample_delivery, NotificationType.DELIVERY_CREATED)
    assert str(sample_delivery.id) in result.message
    assert str(sample_delivery.order_id) in result.message

def test_notify_all_types(sample_delivery):
    for n in NotificationType:
        result = notifications_service.notify(sample_delivery, n)
        assert result.type == n




def test_get_notifications_empty():
    assert notifications_service.get_notifications(str(uuid4())) == []

def test_get_notifications_returns_list(sample_delivery):
    notifications_service.notify(sample_delivery, NotificationType.DELIVERY_CREATED)
    notifications_service.notify(sample_delivery, NotificationType.DELIVERY_ASSIGNED)
    result = notifications_service.get_notifications(sample_delivery.id)
    assert len(result) == 2
    assert all(isinstance(n, Notification) for n in result)

def test_get_notifications_correct_delivery(sample_delivery):
    other_delivery = Delivery(
        id=str(uuid4()),
        order_id="202",
        pickup_address="pickup2",
        dropoff_address="dropoff2",
        status=DeliveryStatus.PENDING
    )
    notifications_service.notify(sample_delivery, NotificationType.DELIVERY_CREATED)
    notifications_service.notify(other_delivery, NotificationType.DELIVERY_CREATED)
    result = notifications_service.get_notifications(sample_delivery.id)
    assert all(n.delivery_id == sample_delivery.id for n in result)
    assert all(n.delivery_id != other_delivery.id for n in result)





def test_mark_as_read(sample_delivery, sample_notification):
    result = notifications_service.mark_as_read(sample_delivery.id, sample_notification.id)
    assert result.read == True

def test_mark_as_read_invalid_notification(sample_delivery):
    with pytest.raises(KeyError):
        notifications_service.mark_as_read(sample_delivery.id, str(uuid4()))

def test_mark_as_read_invalid_delivery():
    with pytest.raises(KeyError):
        notifications_service.mark_as_read(str(uuid4()), str(uuid4()))

def test_mark_as_read_persists(sample_delivery, sample_notification):
    notifications_service.mark_as_read(sample_delivery.id, sample_notification.id)
    notifications = notifications_service.get_notifications(sample_delivery.id)
    assert any(n.id == sample_notification.id and n.read for n in notifications)



def test_delete_notification(sample_delivery, sample_notification):
    result = notifications_service.delete_notification(sample_delivery.id, sample_notification.id)
    assert isinstance(result, Notification)
    assert result.id == sample_notification.id

def test_delete_notification_removes_it(sample_delivery, sample_notification):
    notifications_service.delete_notification(sample_delivery.id, sample_notification.id)
    remaining = notifications_service.get_notifications(sample_delivery.id)
    assert not any(n.id == sample_notification.id for n in remaining)

def test_delete_notification_invalid_notification(sample_delivery):
    with pytest.raises(KeyError):
        notifications_service.delete_notification(sample_delivery.id, str(uuid4()))

def test_delete_notification_invalid_delivery():
    with pytest.raises(KeyError):
        notifications_service.delete_notification(str(uuid4()), str(uuid4()))
