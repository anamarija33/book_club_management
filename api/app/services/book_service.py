# =============================================================
# book_service.py — Poslovna logika za knjige
# =============================================================
# Admin upravlja katalogom knjiga (CRUD).
# Svaki prijavljeni korisnik može označiti knjigu kao pročitanu.
#
# Ownership logika:
#   - Kreiranje/brisanje knjiga: samo admin
#   - Označavanje pročitanih: svaki korisnik za sebe
#   - Brisanje knjige koja je current_book nekog kluba → 409
# =============================================================

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.errors import AppError
from app.models.book import Book
from app.models.club import Club
from app.models.user_book import UserBook
from app.repositories import book_repo


async def _get_or_404(db: AsyncSession, book_id: int) -> Book:
    book = await book_repo.get_by_id(db, book_id)
    if not book:
        raise AppError("not_found", "Knjiga nije pronađena.", 404)
    return book


async def list_books(db: AsyncSession) -> list[Book]:
    return await book_repo.get_all(db)


async def get_book(db: AsyncSession, book_id: int) -> Book:
    return await _get_or_404(db, book_id)


async def create_book(db: AsyncSession, title: str, author: str,
                      pages: int, description: str | None) -> Book:
    book = Book(title=title, author=author, pages=pages, description=description)
    return await book_repo.create(db, book)


async def update_book(db: AsyncSession, book_id: int, data: dict) -> Book:
    book = await _get_or_404(db, book_id)
    for field, value in data.items():
        if value is not None:
            setattr(book, field, value)
    await db.flush()
    return book


async def delete_book(db: AsyncSession, book_id: int) -> None:
    """
    Admin briše knjigu.
    Eager load clubs relacije da izbjegnemo MissingGreenlet.
    Ako je knjiga current_book nekog kluba → 409.
    """
    result = await db.execute(
        select(Book)
        .options(selectinload(Book.clubs))
        .where(Book.id == book_id)
    )
    book = result.scalar_one_or_none()
    if not book:
        raise AppError("not_found", "Knjiga nije pronađena.", 404)
    if book.clubs:
        raise AppError(
            "book_in_use",
            "Knjiga je trenutno dodijeljena klubu — uklonite je iz kluba prije brisanja.",
            409,
        )
    await db.delete(book)


# ---- Pročitane knjige ----

async def get_my_books(db: AsyncSession, user_id: int) -> list[UserBook]:
    return await book_repo.get_user_books(db, user_id)


async def mark_read(db: AsyncSession, user_id: int, book_id: int) -> UserBook:
    await _get_or_404(db, book_id)
    existing = await book_repo.get_user_book(db, user_id, book_id)
    if existing:
        raise AppError("already_read", "Knjiga je već označena kao pročitana.", 409)
    user_book = UserBook(user_id=user_id, book_id=book_id)
    return await book_repo.mark_read(db, user_book)


async def unmark_read(db: AsyncSession, user_id: int, book_id: int) -> None:
    user_book = await book_repo.get_user_book(db, user_id, book_id)
    if not user_book:
        raise AppError("not_found", "Knjiga nije označena kao pročitana.", 404)
    await book_repo.unmark_read(db, user_book)