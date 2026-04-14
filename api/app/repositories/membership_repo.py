# =============================================================
# membership_repo.py — DB upiti za Membership model
# =============================================================

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.membership import Membership


async def get_by_club(
    db: AsyncSession, club_id: int
) -> list[Membership]:
    """Sve prijave za klub s eager-loadanim userom."""
    result = await db.execute(
        select(Membership)
        .options(selectinload(Membership.user))
        .where(Membership.club_id == club_id)
        .order_by(Membership.created_at)
    )
    return list(result.scalars().all())


async def get_by_user(
    db: AsyncSession, user_id: int
) -> list[Membership]:
    """Sve prijave jednog korisnika."""
    result = await db.execute(
        select(Membership)
        .options(selectinload(Membership.club))
        .where(Membership.user_id == user_id)
        .order_by(Membership.created_at)
    )
    return list(result.scalars().all())


async def get_by_id(
    db: AsyncSession, membership_id: int
) -> Membership | None:
    result = await db.execute(
        select(Membership)
        .options(selectinload(Membership.user), selectinload(Membership.club))
        .where(Membership.id == membership_id)
    )
    return result.scalar_one_or_none()


async def get_existing(
    db: AsyncSession, user_id: int, club_id: int
) -> Membership | None:
    """Provjeri postoji li već prijava za tu kombinaciju."""
    result = await db.execute(
        select(Membership).where(
            Membership.user_id == user_id,
            Membership.club_id == club_id,
        )
    )
    return result.scalar_one_or_none()


async def count_approved(db: AsyncSession, club_id: int) -> int:
    """Broj odobrenih članova u klubu."""
    result = await db.execute(
        select(func.count()).where(
            Membership.club_id == club_id,
            Membership.status == "approved",
        )
    )
    return result.scalar_one()


async def create(db: AsyncSession, membership: Membership) -> Membership:
    db.add(membership)
    await db.flush()
    return membership
