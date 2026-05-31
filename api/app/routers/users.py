from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_db, require_role
from app.models.user import User
from app.schemas.auth import UserResponse
from app.schemas.user import UserCreate, UserSelfUpdate, UserUpdate
from app.services import user_service

router = APIRouter()


@router.get("/", response_model=list[UserResponse])
async def list_users(
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_role("admin")),
):
    return await user_service.list_users(db)


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    body: UserCreate,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_role("admin")),
):
    return await user_service.create_user(
        db,
        username=body.username,
        email=body.email,
        password=body.password,
        role=body.role,
        is_active=body.is_active,
        hours_per_week=body.hours_per_week,
        pages_per_week=body.pages_per_week,
    )


# /me/profile must come BEFORE /{user_id} — Starlette matches in registration order
# and /{user_id: int} would 422 on "me" before reaching this route if declared after.
@router.patch("/me/profile", response_model=UserResponse)
async def update_my_profile(
    body: UserSelfUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await user_service.self_update(
        db,
        current_user=current_user,
        email=body.email,
        password=body.password,
        hours_per_week=body.hours_per_week,
        pages_per_week=body.pages_per_week,
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_role("admin")),
):
    return await user_service.get_user(db, user_id)


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    body: UserUpdate,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_role("admin")),
):
    return await user_service.update_user(
        db,
        user_id=user_id,
        username=body.username,
        email=body.email,
        password=body.password,
        role=body.role,
        is_active=body.is_active,
        hours_per_week=body.hours_per_week,
        pages_per_week=body.pages_per_week,
    )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_role("admin")),
):
    await user_service.delete_user(db, user_id)
