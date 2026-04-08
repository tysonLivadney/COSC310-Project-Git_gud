import uuid
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from fastapi import HTTPException
from schemas.promo_code import PromoCode, PromoCodeCreate, DiscountType
from repositories.promo_codes_repo import load_all, save_all

two_places = Decimal("0.01")


def create_promo_code(payload: PromoCodeCreate) -> PromoCode:
    codes = load_all()

    # make sure code doesnt already exist
    for c in codes:
        if c["code"].lower() == payload.code.strip().lower():
            raise HTTPException(status_code=409, detail="Promo code already exists")

    new_id = str(uuid.uuid4())
    promo = PromoCode(
        id=new_id,
        code=payload.code.strip().upper(),
        discount_type=payload.discount_type,
        discount_value=payload.discount_value,
        expiry_date=payload.expiry_date,
        max_uses=payload.max_uses,
        min_order_amount=payload.min_order_amount,
        usage_count=0,
        active=True,
        created_at=datetime.now(timezone.utc).isoformat(),
    )

    codes.append(promo.model_dump())
    save_all(codes)
    return promo


def list_promo_codes() -> list:
    return [PromoCode(**c) for c in load_all()]


def get_promo_code(code: str) -> PromoCode:
    for c in load_all():
        if c["code"].lower() == code.strip().lower():
            return PromoCode(**c)
    raise HTTPException(status_code=404, detail="Promo code not found")


def validate_promo_code(code: str, order_subtotal: float) -> PromoCode:
    promo = get_promo_code(code)

    if not promo.active:
        raise HTTPException(status_code=400, detail="This promo code is no longer active")

    # check if expired
    if promo.expiry_date:
        expiry = datetime.fromisoformat(promo.expiry_date)
        now = datetime.now(timezone.utc)
        # make expiry timezone aware if it isnt
        if expiry.tzinfo is None:
            expiry = expiry.replace(tzinfo=timezone.utc)
        if now > expiry:
            raise HTTPException(status_code=400, detail="This promo code has expired")

    # check usage limit
    if promo.max_uses is not None and promo.usage_count >= promo.max_uses:
        raise HTTPException(status_code=400, detail="This promo code has reached its usage limit")

    # check minimum order amount
    if promo.min_order_amount is not None and order_subtotal < promo.min_order_amount:
        raise HTTPException(
            status_code=400,
            detail=f"Order must be at least ${promo.min_order_amount} to use this code"
        )

    return promo


def calculate_discount(promo: PromoCode, subtotal: Decimal) -> Decimal:
    if promo.discount_type == DiscountType.PERCENTAGE:
        discount = subtotal * Decimal(str(promo.discount_value)) / Decimal("100")
    else:
        discount = Decimal(str(promo.discount_value))

    # dont let discount go over the subtotal
    if discount > subtotal:
        discount = subtotal

    return discount.quantize(two_places, rounding=ROUND_HALF_UP)


def increment_usage(code: str) -> None:
    codes = load_all()
    for c in codes:
        if c["code"].lower() == code.strip().lower():
            c["usage_count"] = c.get("usage_count", 0) + 1
            save_all(codes)
            return


def deactivate_promo_code(code: str) -> PromoCode:
    codes = load_all()
    for c in codes:
        if c["code"].lower() == code.strip().lower():
            c["active"] = False
            save_all(codes)
            return PromoCode(**c)
    raise HTTPException(status_code=404, detail="Promo code not found")
