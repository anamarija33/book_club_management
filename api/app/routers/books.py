# =============================================================
# routers/books.py — Book endpointi
# =============================================================
# GET    /books/                    — katalog (svi prijavljeni)
# POST   /books/                    — dodaj knjigu (admin)
# GET    /books/{id}                — detalji (svi prijavljeni)
# PATCH  /books/{id}                — ažuriraj (admin)
# DELETE /books/{id}                — obriši (admin)
#
# GET    /users/me/books            — moje pročitane knjige
# POST   /users/me/books/{book_id}  — označi kao pročitanu
# DELETE /users/me/books/{book_id}  — ukloni oznaku
# =============================================================

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_db, require_role
from app.models.user import User
from app.schemas.book import BookCreate, BookResponse, BookUpdate, UserBookResponse
from app.services import book_service

router = APIRouter()


# ---- Katalog knjiga ----

@router.get("/books", response_model=list[BookResponse], tags=["books"])
async def list_books(
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    """Katalog svih knjiga — svi prijavljeni korisnici."""
    return await book_service.list_books(db)


@router.post(
    "/books",
    response_model=BookResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["books"],
)
async def create_book(
    body: BookCreate,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_role("admin")),
):
    """Admin dodaje novu knjigu u katalog."""
    return await book_service.create_book(
        db,
        title=body.title,
        author=body.author,
        pages=body.pages,
        description=body.description,
    )


@router.get("/books/{book_id}", response_model=BookResponse, tags=["books"])
async def get_book(
    book_id: int,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    return await book_service.get_book(db, book_id)


@router.patch("/books/{book_id}", response_model=BookResponse, tags=["books"])
async def update_book(
    book_id: int,
    body: BookUpdate,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_role("admin")),
):
    return await book_service.update_book(
        db, book_id, body.model_dump(exclude_none=True)
    )


@router.delete(
    "/books/{book_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["books"],
)
async def delete_book(
    book_id: int,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_role("admin")),
):
    await book_service.delete_book(db, book_id)


# ---- Pročitane knjige korisnika ----

@router.get(
    "/users/me/books",
    response_model=list[UserBookResponse],
    tags=["books"],
)
async def my_books(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lista knjiga koje je prijavljeni korisnik pročitao."""
    return await book_service.get_my_books(db, current_user.id)


@router.post(
    "/users/me/books/{book_id}",
    response_model=UserBookResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["books"],
)
async def mark_read(
    book_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Označi knjigu kao pročitanu."""
    return await book_service.mark_read(db, current_user.id, book_id)


@router.delete(
    "/users/me/books/{book_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["books"],
)
async def unmark_read(
    book_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Ukloni oznaku pročitane knjige."""
    await book_service.unmark_read(db, current_user.id, book_id)
