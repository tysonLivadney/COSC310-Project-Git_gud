import pytest
from services import delivery_service
from schemas import Driver, DriverStatus
from repositories.delivery_repo import save_all as save_delivery,load_all as load_delivery

@pytest.fixture
def valid_driver():
    return Driver(
        id="1",
        name="John Smith",
        phone="+123456789",
        status=DriverStatus.ONLINE
    )
    
def save_and_restore():
    deliveries = load_delivery()
    save_delivery([])
    yield
    save_delivery(deliveries)
