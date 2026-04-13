# =============================================================
# club_service.py — Poslovna logika za upravljanje klubovima
# =============================================================
# Ovaj sloj NE zna za HTTP — prima domenske objekte,
# vraća domenske objekte ili baca AppError.
#
# Ownership logika:
#   - Admin vidi i mijenja sve klubove
#   - Member vidi samo klubove u kojima je član (dolazi s membershipima)
#   - Kreiranje i brisanje — samo admin
# =============================================================

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.models.club import Club
from app.models.user import User
from app.repositories import club_repo


async def _get_or_404(db: AsyncSession, club_id: int) -> Club:
    club = await club_repo.get_by_id(db, club_id)
    if not club:
        raise AppError("not_found", "Klub nije pronađen.", 404)
    return club


async def list_clubs(db: AsyncSession, current_user: User) -> list[Club]:
    return await club_repo.get_all(db)


async def get_club(db: AsyncSession, club_id: int, current_user: User) -> Club:
    return await _get_or_404(db, club_id)


async def create_club(
    db: AsyncSession,
    name: str,
    description: str | None,
    max_members: int,
    min_hours_per_week: float,
    pages_per_week: int,
    registration_deadline,
    admin_id: int,
) -> Club:
    existing = await club_repo.get_by_name(db, name)
    if existing:
        raise AppError("duplicate", f"Klub '{name}' već postoji.", 409)

    club = Club(
        name=name,
        description=description,
        max_members=max_members,
        min_hours_per_week=min_hours_per_week,
        pages_per_week=pages_per_week,
        registration_deadline=registration_deadline,
        created_by=admin_id,
    )
    return await club_repo.create(db, club)


async def update_club(
    db: AsyncSession,
    club_id: int,
    current_user: User,
    name: str | None,
    description: str | None,
    max_members: int | None,
    min_hours_per_week: float | None,
    pages_per_week: int | None,
    registration_deadline=None,
) -> Club:
    club = await _get_or_404(db, club_id)

    if name is not None and name != club.name:
        existing = await club_repo.get_by_name(db, name)
        if existing:
            raise AppError("duplicate", f"Klub '{name}' već postoji.", 409)
        club.name = name

    if description is not None:
        club.description = description
    if max_members is not None:
        club.max_members = max_members
    if min_hours_per_week is not None:
        club.min_hours_per_week = min_hours_per_week
    if pages_per_week is not None:
        club.pages_per_week = pages_per_week
    if registration_deadline is not None:
        club.registration_deadline = registration_deadline

    await db.flush()
    return club


async def delete_club(db: AsyncSession, club_id: int) -> None:
    club = await _get_or_404(db, club_id)
    await db.delete(club)
    await db.flush()