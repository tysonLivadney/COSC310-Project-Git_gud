from collections.abc import Callable
from fastapi import Depends, Header, HTTPException
from repositories.users_repo import load_all as load_all_users
from schemas.auth import Role, UserResponse
from services.auth_service import build_user_response
from services.session_service import resolve_session


def _extract_bearer_token(authorization: str | None) -> str:
    if not authorization:
        raise HTTPException(status_code=401, detail="Authentication required")
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    return token.strip()


def get_current_user(authorization: str | None = Header(default=None)) -> UserResponse:
    token = _extract_bearer_token(authorization)
    user_id = resolve_session(token)
    users = load_all_users()
    for user in users:
        if user["id"] == user_id:
            return build_user_response(user)
    raise HTTPException(status_code=404, detail="User not found")


def require_roles(*allowed_roles: Role) -> Callable[[UserResponse], UserResponse]:
    def role_checker(current_user: UserResponse = Depends(get_current_user)) -> UserResponse:
        if current_user.role not in allowed_roles:
            raise HTTPException(status_code=403, detail="You do not have permission to perform this action")
        return current_user
    return role_checker
