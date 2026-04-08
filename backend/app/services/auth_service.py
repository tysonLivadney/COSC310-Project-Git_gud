import uuid
from datetime import datetime, timezone
from fastapi import HTTPException
from repositories.users_repo import load_all as load_all_users
from repositories.drivers_repo import load_all as load_all_drivers                              
from repositories.drivers_repo import save_all as save_all_drivers 
from repositories.users_repo import save_all as save_all_users
from schemas.auth import LoginRequest, LoginResponse, RegisterRequest, UserResponse
from services.password_service import generate_salt, hash_password, verify_password
from services.session_service import create_session


def _utc_now_string() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _normalize_email(email: str) -> str:
    return email.strip().lower()


def _find_user_by_email(users: list[dict], normalized_email: str) -> dict | None:
    for user in users:
        if _normalize_email(user["email"]) == normalized_email:
            return user
    return None


def build_user_response(user: dict) -> UserResponse:
    return UserResponse(
        id=user["id"],
        name=user["name"],
        email=user["email"],
        role=user["role"],
        created_at=user["created_at"],
        address=user.get("address"),
    )


def register_user(payload: RegisterRequest) -> UserResponse:
    users = load_all_users()
    normalized_email = _normalize_email(payload.email)

    if any(_normalize_email(u["email"]) == normalized_email for u in users):
        raise HTTPException(status_code=400, detail="An account with that email already exists")

    salt_hex = generate_salt()
    user = {
        "id": str(uuid.uuid4()),
        "name": payload.name.strip(),
        "email": normalized_email,
        "role": payload.role,
        "password_salt": salt_hex,
        "password_hash": hash_password(payload.password, salt_hex),
        "created_at": _utc_now_string(),
        "address": payload.address,
    }
    users.append(user)
    save_all_users(users)

    if payload.role == "driver":
        drivers = load_all_drivers()
        drivers.append({
            "user_id": user["id"],
            "name": user["name"],
            "phone": "",
            "vehicle_type": "",
            "license_plate": "",
            "available": True,
        })
        save_all_drivers(drivers)

    return build_user_response(user)


def login_user(payload: LoginRequest) -> LoginResponse:
    users = load_all_users()
    normalized_email = _normalize_email(payload.email)

    user = _find_user_by_email(users, normalized_email)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not verify_password(payload.password, user["password_salt"], user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    session = create_session(user["id"])

    return LoginResponse(
        token=session["token"],
        token_type="bearer",
        expires_at=session["expires_at"],
        user=build_user_response(user),
    )
