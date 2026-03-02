from .delivery import Delivery, DeliveryStatus
from .driver import Driver, DriverStatus

Driver.model_rebuild()
Delivery.model_rebuild()