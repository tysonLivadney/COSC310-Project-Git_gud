from pydantic import BaseModel, field_validator
from typing import Literal, Optional


Role = Literal["user", "owner", "manager", "driver"]


class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str
    role: Role
    address: Optional[str] = None

    @field_validator("name", "password")
    @classmethod
    def validate_non_empty_fields(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Field cannot be empty")
        return value

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        cleaned = value.strip()
        if "@" not in cleaned or cleaned.startswith("@") or cleaned.endswith("@"):
            raise ValueError("Invalid email address")
        return cleaned


class LoginRequest(BaseModel):
    email: str
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Field cannot be empty")
        return value

    @field_validator("email")
    @classmethod
    def validate_login_email(cls, value: str) -> str:
        cleaned = value.strip()
        if "@" not in cleaned or cleaned.startswith("@") or cleaned.endswith("@"):
            raise ValueError("Invalid email address")
        return cleaned


class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    role: Role
    created_at: str
    address: Optional[str] = None


class LoginResponse(BaseModel):
    token: str
    token_type: str
    expires_at: str
    user: UserResponse
