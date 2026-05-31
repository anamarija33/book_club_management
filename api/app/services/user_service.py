from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.core.security import hash_password
from app.models.user import User
from app.repositories import user_repo


async def _get_or_404(db: AsyncSession, user_id: int) -> User:
    user = await user_repo.get_by_id(db, user_id)
    if not user:
        raise AppError("not_found", "Korisnik nije pronađen.", 404)
    return user


async def list_users(db: AsyncSession) -> list[User]:
    return await user_repo.get_all(db)


async def get_user(db: AsyncSession, user_id: int) -> User:
    return await _get_or_404(db, user_id)


async def create_user(
    db: AsyncSession,
    username: str,
    email: str,
    password: str,
    role: str,
    is_active: bool,
    hours_per_week: float,
    pages_per_week: int,
) -> User:
    if await user_repo.get_by_username(db, username):
        raise AppError("duplicate", f"Korisničko ime '{username}' već postoji.", 409)
    if await user_repo.get_by_email(db, email):
        raise AppError("duplicate", "Email adresa već postoji.", 409)
    user = User(
        username=username,
        email=email,
        password_hash=hash_password(password),
        role=role,
        is_active=is_active,
        hours_per_week=hours_per_week,
        pages_per_week=pages_per_week,
    )
    return await user_repo.create(db, user)


async def update_user(
    db: AsyncSession,
    user_id: int,
    username: str | None,
    email: str | None,
    password: str | None,
    role: str | None,
    is_active: bool | None,
    hours_per_week: float | None,
    pages_per_week: int | None,
) -> User:
    user = await _get_or_404(db, user_id)

    if username is not None and username != user.username:
        if await user_repo.get_by_username(db, username):
            raise AppError("duplicate", f"Korisničko ime '{username}' već postoji.", 409)
        user.username = username

    if email is not None and email != user.email:
        if await user_repo.get_by_email(db, email):
            raise AppError("duplicate", "Email adresa već postoji.", 409)
        user.email = email

    if password is not None:
        user.password_hash = hash_password(password)
    if role is not None:
        user.role = role
    if is_active is not None:
        user.is_active = is_active
    if hours_per_week is not None:
        user.hours_per_week = hours_per_week
    if pages_per_week is not None:
        user.pages_per_week = pages_per_week

    await db.flush()
    return user


async def delete_user(db: AsyncSession, user_id: int) -> None:
    user = await _get_or_404(db, user_id)
    await db.delete(user)
    await db.flush()


async def self_update(
    db: AsyncSession,
    current_user: User,
    email: str | None,
    password: str | None,
    hours_per_week: float | None,
    pages_per_week: int | None,
) -> User:
    if email is not None and email != current_user.email:
        if await user_repo.get_by_email(db, email):
            raise AppError("duplicate", "Email adresa već postoji.", 409)
        current_user.email = email

    if password is not None:
        current_user.password_hash = hash_password(password)
    if hours_per_week is not None:
        current_user.hours_per_week = hours_per_week
    if pages_per_week is not None:
        current_user.pages_per_week = pages_per_week

    await db.flush()
    return current_user
