from fastapi import APIRouter, Depends, status
from schemas.review import Review, ReviewCreate
from schemas.auth import UserResponse
from services.auth_service import get_current_user
from services.reviews_service import create_review

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.post("", response_model=Review, status_code=status.HTTP_201_CREATED)
def post_review(
    payload: ReviewCreate,
    current_user: UserResponse = Depends(get_current_user),
):
    return create_review(payload, current_user.id)
