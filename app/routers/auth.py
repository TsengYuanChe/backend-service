from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from app.core.security import create_access_token, verify_password
from app.database import SessionLocal
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse
from app.dependencies.auth import get_current_user
from app.schemas.user import UserResponse

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest):
    with SessionLocal() as session:
        user = session.scalar(
            select(User).where(
                User.account_name == request.account_name
            )
        )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid account name or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid account name or password",
        )

    if not verify_password(
        request.password,
        user.password_hash,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid account name or password",
        )

    token = create_access_token(user.id)

    return TokenResponse(
        access_token=token,
    )
    
    
@router.get("/me", response_model=UserResponse)
def get_me(
    current_user: User = Depends(get_current_user),
):
    return current_user

