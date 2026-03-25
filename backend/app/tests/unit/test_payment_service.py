from decimal import Decimal
from fastapi import HTTPException
from schemas.payment import PaymentProcessRequest, PaymentInfo
from services.payment_service import PaymentService
from repositories.payments_repo import load_all, save_all
import pytest

@pytest.fixture(autouse = True)
def save_and_restore():
    payments = load_all()
    save_all([])
    yield
    save_all(payments)



VALID_PAYMENT_INFO = {
    "card_number": "2121000000000000",
    "cvv": "123",
    "expiry": "12/30"
}

def make_request(order_id="order-123", total="25.00", **payment_info):
    payment_info = {**VALID_PAYMENT_INFO, **payment_info}
    return PaymentProcessRequest(
        order_id=order_id,
        total=Decimal(total), 
        payment_info=PaymentInfo(**payment_info)
    )

def test_process_payment_aprroved():
    request = make_request()
    response = PaymentService.process_payment(request)
    assert response.order_id == "order-123"
    assert response.status == "approved"
    assert response.message == "Payment approved!"
    assert response.payment_id is not None

def test_process_payment_invalid_card():
    request = make_request(card_number="4536001274011809")
    try:
        PaymentService.process_payment(request)
        assert False, "HTTPException is expected to be raised"
    except HTTPException as e:
        assert e.status_code == 402
        assert e.detail == "Invalid card number!"

def test_list_payments_returns_saved_payment():
    request = make_request(order_id="order-456")
    PaymentService.process_payment(request)
    payments = PaymentService.list_payments()
    assert len(payments) == 1
    assert payments[0].order_id == "order-456"
    assert payments[0].status == "approved"

def test_get_payment_by_id():
    request = make_request(order_id="order-789")
    response = PaymentService.process_payment(request)
    payment_id = response.payment_id
    payment = PaymentService.get_payment_by_id(payment_id)
    assert payment is not None
    assert payment.id == payment_id
    assert payment.order_id == "order-789"

def test_get_payment_by_id_not_found():
    payment = PaymentService.get_payment_by_id("Invalid-id")
    assert payment is None