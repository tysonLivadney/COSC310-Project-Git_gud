from fastapi import HTTPException
from schemas.driver_profile import DriverProfile, DriverProfileCreate, DriverProfileUpdate
from repositories.drivers_repo import load_all, save_all


def create_driver_profile(user_id: str, name: str, payload: DriverProfileCreate) -> DriverProfile:
    drivers = load_all()

    if any(d.get("user_id") == user_id for d in drivers):
        raise HTTPException(status_code=409, detail="Driver profile already exists")

    profile = DriverProfile(
        user_id=user_id,
        name=name,
        phone=payload.phone,
        vehicle_type=payload.vehicle_type,
        license_plate=payload.license_plate,
    )
    drivers.append(profile.model_dump())
    save_all(drivers)
    return profile


def get_driver_profile(user_id: str) -> DriverProfile:
    drivers = load_all()
    for d in drivers:
        if d.get("user_id") == user_id:
            return DriverProfile(**d)
    raise HTTPException(status_code=404, detail="Driver profile not found")


def update_driver_profile(user_id: str, payload: DriverProfileUpdate) -> DriverProfile:
    drivers = load_all()
    for idx, d in enumerate(drivers):
        if d.get("user_id") == user_id:
            current = DriverProfile(**d)
            updated = DriverProfile(
                user_id=current.user_id,
                name=current.name,
                phone=payload.phone if payload.phone is not None else current.phone,
                vehicle_type=payload.vehicle_type if payload.vehicle_type is not None else current.vehicle_type,
                license_plate=payload.license_plate if payload.license_plate is not None else current.license_plate,
                available=payload.available if payload.available is not None else current.available,
            )
            drivers[idx] = updated.model_dump()
            save_all(drivers)
            return updated
    raise HTTPException(status_code=404, detail="Driver profile not found")


def list_available_drivers():
    drivers = load_all()
    return [DriverProfile(**d) for d in drivers if d.get("available")]
