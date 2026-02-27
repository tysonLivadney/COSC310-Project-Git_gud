import uuid 
import re
from datetime import datetime
from typing import List

from ..schemas.payment import (
    PaymentProcessRequest,
    PaymentProcessResponse,
    PaymentRecord,
)

from ..repositories.payments_repo import load_all, save_all

class PaymentValidator:
    # Luhn algorithm implementation for card number validation
    @staticmethod
    def luhn_check(card_number: str) -> bool:
        card_number = card_number.strip()
        digit = [int(d) for d in card_number if d.isdigit()]
        if len(digit) < 13 or len(digit) > 19:
            return False
        total = sum(digit[-1::-2]) + sum((2 * d // 10 + 2 * d % 10) if 2 * d > 9 else 2 * d for d in digit[-2::-2])
        return total % 10 == 0
    
    # Validation steps for payment processing
    @staticmethod
    def validate(req: PaymentProcessRequest) -> tuple[str, str]:
        card = req.payment_info.card_number.strip()
        cvv = req.payment_info.cvv.strip()
        expiry = req.payment_info.expiry.strip()

        # Total amount check
        if req.total <= 0:
            return ("declined", "Invalid balance!")
        # Card number check using Luhn method
        if not card.isdigit() or not (13 <= len(card) <= 19) or not PaymentValidator.luhn_check(card):
            return ("declined", "Invalid card number!")
        # CVV must be 3 or 4 digits
        if not cvv.isdigit() or len(cvv) not in (3, 4):
            return ("declined", "Invalid CVV!")
        # Expiry date format check
        if not re.match(r"^(0[1-9]|1[0-2])\/\d{2}$", expiry):
            return ("declined", "Invalid expiry date format!")
        
        month, year = expiry.split("/")
        exp_date = datetime(int("20" + year), int(month), 1)
        now = datetime.now()
        current_month = datetime(now.year, now.month, 1)

        # Expiry date check
        if exp_date < current_month:
            return ("declined", "Card has expired!")
        
        # All check pass -> return approved
        return ("approved", "Payment approved!")
    
    @staticmethod
    def process_payment(req: PaymentProcessRequest) -> PaymentProcessResponse:
        payments = load_all()
        payment_id = str(uuid.uuid4())

        if any(p.get("id") == payment_id for p in payments):
            return PaymentProcessResponse(
                payment_id="",
                order_id=req.order_id,
                status="declined",
                message="ID collision; retry."
            )
        status, message = PaymentValidator.validate(req)
        record = PaymentRecord(
            id = payment_id,
            order_id = req.order_id,
            total = req.total,
            status = status,
            message = message
        )
        payments.append(record.dict())
        save_all(payments)
        return PaymentProcessResponse(
            payment_id=record.id,
            order_id=req.order_id,
            status=status,
            message=message
        )
    
    @staticmethod
    def list_payments() -> List[PaymentRecord]:
        return [PaymentRecord(**p) for p in load_all()]
    
    @staticmethod
    def get_payment_by_id(payment_id: str) -> PaymentRecord | None:
        for p in load_all():
            if p.get("id") == payment_id:
                return PaymentRecord(**p)
        return None
    
process_payment = PaymentValidator.process_payment
list_payments = PaymentValidator.list_payments
get_payment_by_id = PaymentValidator.get_payment_by_id