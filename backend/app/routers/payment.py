from fastapi import APIRouter, HTTPException
from typing import List

from schemas.payment import (
    PaymentProcessRequest,
    PaymentProcessResponse,
    PaymentRecord,
)
from services.payment_service import (
    process_payment,
    list_payments,
    get_payment_by_id,
)

router = APIRouter(prefix="/payments", tags=["payments"])

@router.post("/process", response_model=PaymentProcessResponse, responses = { 402: {"description": "Payment declined"}})
def process(payload: PaymentProcessRequest):
    return process_payment(payload)

@router.get("", response_model=List[PaymentRecord])
def get_all():
    return list_payments()

@router.get("/by-order/{order_id}", response_model=List[PaymentRecord])
def get_by_orderID(order_id: str):
    payments = list_payments()
    return [p for p in payments if p.order_id == order_id]

@router.get("/by-payment/{payment_id}", response_model=PaymentRecord)
def get_by_paymentID(payment_id: str):
    payment = get_payment_by_id(payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment