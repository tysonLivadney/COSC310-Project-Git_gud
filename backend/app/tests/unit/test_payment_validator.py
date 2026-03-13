from decimal import Decimal
from schemas.payment import PaymentProcessRequest, PaymentInfo
from services.payment_validator import PaymentValidator

VALID_PAYMENT_INFO = {
    "card_number": "2121000000000000",
    "cvv": "123",
    "expiry": "12/30"
}

def make_request(total="25.00", **payment_info):
    payment_info = {**VALID_PAYMENT_INFO, **payment_info}
    return PaymentProcessRequest(
        order_id="order-123",
        total=Decimal(total), 
        payment_info=PaymentInfo(**payment_info)
    )

def test_luhn_check_card_valid():
    assert PaymentValidator.luhn_check("2121000000000000") == True

def test_luhn_check_card_invalid():
    assert PaymentValidator.luhn_check("4536001274011809") == False

def test_validate_approved_payment():
    request = make_request()
    status, message = PaymentValidator.validate(request)
    assert status == "approved"
    assert message == "Payment approved!"

def test_validate_declined_total_balance():
    request = make_request(total="-5.00")
    status, message = PaymentValidator.validate(request)
    assert status == "declined"
    assert message == "Invalid balance!"

def test_validate_declined_card_number():
    request = make_request(card_number="4536001274011809")
    status, message = PaymentValidator.validate(request)
    assert status == "declined"
    assert message == "Invalid card number!"

def test_validate_declined_expired_card():
    request = make_request(expiry="09/19")
    status, message = PaymentValidator.validate(request)
    assert status == "declined"
    assert message == "Card has expired!"