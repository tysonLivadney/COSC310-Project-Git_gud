from fastapi import APIRouter, Depends, status

from dependencies import get_auth_service, get_current_user
from schemas.auth import LoginRequest, LoginResponse, RegisterRequest, UserResponse
from services.auth_service import AuthService


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    payload: RegisterRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    return auth_service.register_user(payload)


@router.post("/login", response_model=LoginResponse)
def login(
    payload: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    return auth_service.login_user(payload)


@router.get("/me", response_model=UserResponse)
def me(current_user: UserResponse = Depends(get_current_user)):
    return current_user
