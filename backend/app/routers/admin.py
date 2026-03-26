from fastapi import APIRouter, Depends
from typing import List, Optional
from schemas.order import Order, OrderStatus
from schemas.admin import AdminReport
from schemas.auth import UserResponse
from services.auth_dependencies import require_roles
from services.admin_service import list_all_orders, generate_report

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/orders", response_model=List[Order])
def get_all_orders(
    customer_id: Optional[str] = None,
    restaurant_id: Optional[int] = None,
    status: Optional[OrderStatus] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    current_user: UserResponse = Depends(require_roles("manager")),
):
    return list_all_orders(
        customer_id=customer_id,
        restaurant_id=restaurant_id,
        status=status,
        date_from=date_from,
        date_to=date_to,
    )


@router.get("/reports", response_model=AdminReport)
def get_reports(
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    current_user: UserResponse = Depends(require_roles("manager")),
):
    return generate_report(date_from=date_from, date_to=date_to)
