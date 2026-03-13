import uuid
from typing import List
from fastapi import HTTPException
from repositories.payments_repo import load_all, save_all
from services.payment_validator import PaymentValidator

from schemas.payment import (
    PaymentProcessRequest,
    PaymentProcessResponse,
    PaymentRecord,
)

class PaymentService:
    @staticmethod
    def process_payment(req: PaymentProcessRequest) -> PaymentProcessResponse:
        payments = load_all()
        payment_id = str(uuid.uuid4())
        status, message = PaymentValidator.validate(req)
        record = PaymentRecord(
            id=payment_id,
            order_id=req.order_id,
            total=req.total,
            status=status,
            message=message
        )
        payments.append(record.model_dump(mode = "json"))
        save_all(payments)

        ## If declined, raise a HTTP error wit the message
        if status == "declined":
            raise HTTPException(status_code=402, detail=message)
        
        ## Approved card return
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

process_payment = PaymentService.process_payment
list_payments = PaymentService.list_payments
get_payment_by_id = PaymentService.get_payment_by_id
