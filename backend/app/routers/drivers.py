from fastapi import APIRouter, Depends
from typing import List
from schemas.driver_profile import DriverProfile, DriverProfileCreate, DriverProfileUpdate
from schemas.auth import UserResponse
from services.auth_service import require_roles
from services.drivers_service import (
    create_driver_profile,
    get_driver_profile,
    update_driver_profile,
    list_available_drivers,
)

router = APIRouter(prefix="/drivers", tags=["drivers"])


@router.post("/profile", response_model=DriverProfile, status_code=201)
def create_profile(
    payload: DriverProfileCreate,
    current_user: UserResponse = Depends(require_roles("driver")),
):
    return create_driver_profile(current_user.id, current_user.name, payload)


@router.get("/profile", response_model=DriverProfile)
def get_profile(
    current_user: UserResponse = Depends(require_roles("driver")),
):
    return get_driver_profile(current_user.id)


@router.put("/profile", response_model=DriverProfile)
def update_profile(
    payload: DriverProfileUpdate,
    current_user: UserResponse = Depends(require_roles("driver")),
):
    return update_driver_profile(current_user.id, payload)


@router.get("/available", response_model=List[DriverProfile])
def get_available_drivers(
    current_user: UserResponse = Depends(require_roles("manager", "owner")),
):
    return list_available_drivers()
