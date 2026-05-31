from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db, require_role
from app.models.book import Book
from app.models.club import Club
from app.models.membership import Membership
from app.models.user import User

router = APIRouter()


class StatsResponse(BaseModel):
    total_users: int
    total_clubs: int
    total_books: int
    total_memberships: int


@router.get("/", response_model=StatsResponse)
async def get_stats(
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_role("admin")),
):
    async def count(model) -> int:
        result = await db.execute(select(func.count()).select_from(model))
        return result.scalar_one()

    total_users, total_clubs, total_books, total_memberships = (
        await count(User),
        await count(Club),
        await count(Book),
        await count(Membership),
    )
    return StatsResponse(
        total_users=total_users,
        total_clubs=total_clubs,
        total_books=total_books,
        total_memberships=total_memberships,
    )
