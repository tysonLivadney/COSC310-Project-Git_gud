from fastapi import APIRouter, Depends
from typing import List
from schemas.promo_code import PromoCode, PromoCodeCreate, PromoCodeValidateRequest
from schemas.auth import UserResponse
from services.auth_dependencies import require_roles
from services.promo_code_service import (
    create_promo_code,
    list_promo_codes,
    validate_promo_code,
    deactivate_promo_code,
)

router = APIRouter(prefix="/promo-codes", tags=["promo-codes"])


@router.post("", response_model=PromoCode, status_code=201)
def post_promo_code(
    payload: PromoCodeCreate,
    current_user: UserResponse = Depends(require_roles("manager")),
):
    return create_promo_code(payload)


@router.get("", response_model=List[PromoCode])
def get_promo_codes(
    current_user: UserResponse = Depends(require_roles("manager")),
):
    return list_promo_codes()


@router.post("/validate")
def post_validate_promo_code(payload: PromoCodeValidateRequest):
    promo = validate_promo_code(payload.code, payload.order_subtotal)
    return {"valid": True, "promo_code": promo}


@router.delete("/{code}", response_model=PromoCode)
def delete_promo_code(
    code: str,
    current_user: UserResponse = Depends(require_roles("manager")),
):
    return deactivate_promo_code(code)
