# =============================================================
# book_repo.py — DB upiti za Book i UserBook modele
# =============================================================

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.book import Book
from app.models.user_book import UserBook


async def get_all(db: AsyncSession) -> list[Book]:
    result = await db.execute(select(Book).order_by(Book.title))
    return list(result.scalars().all())


async def get_by_id(db: AsyncSession, book_id: int) -> Book | None:
    result = await db.execute(select(Book).where(Book.id == book_id))
    return result.scalar_one_or_none()


async def create(db: AsyncSession, book: Book) -> Book:
    db.add(book)
    await db.flush()
    return book


async def delete(db: AsyncSession, book: Book) -> None:
    await db.delete(book)


# ---- UserBook ----

async def get_user_books(db: AsyncSession, user_id: int) -> list[UserBook]:
    """Eager load book relaciju da izbjegnemo MissingGreenlet."""
    result = await db.execute(
        select(UserBook)
        .options(selectinload(UserBook.book))
        .where(UserBook.user_id == user_id)
    )
    return list(result.scalars().all())


async def get_user_book(
    db: AsyncSession, user_id: int, book_id: int
) -> UserBook | None:
    result = await db.execute(
        select(UserBook)
        .options(selectinload(UserBook.book))
        .where(UserBook.user_id == user_id, UserBook.book_id == book_id)
    )
    return result.scalar_one_or_none()


async def mark_read(db: AsyncSession, user_book: UserBook) -> UserBook:
    db.add(user_book)
    await db.flush()
    # Reload s book relacijom za response
    result = await db.execute(
        select(UserBook)
        .options(selectinload(UserBook.book))
        .where(
            UserBook.user_id == user_book.user_id,
            UserBook.book_id == user_book.book_id,
        )
    )
    return result.scalar_one()


async def unmark_read(db: AsyncSession, user_book: UserBook) -> None:
    await db.delete(user_book)