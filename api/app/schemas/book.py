# =============================================================
# schemas/book.py — Pydantic scheme za Book entitet
# =============================================================

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class BookCreate(BaseModel):
    """POST /books — admin dodaje novu knjigu."""
    title: str = Field(min_length=1, max_length=200)
    author: str = Field(min_length=1, max_length=150)
    pages: int = Field(gt=0)
    description: Optional[str] = None


class BookUpdate(BaseModel):
    """PATCH /books/{id} — parcijalni update."""
    title: str | None = Field(default=None, min_length=1, max_length=200)
    author: str | None = Field(default=None, min_length=1, max_length=150)
    pages: int | None = Field(default=None, gt=0)
    description: str | None = None


class BookResponse(BaseModel):
    id: int
    title: str
    author: str
    pages: int
    description: str | None = None

    model_config = {"from_attributes": True}


class UserBookResponse(BaseModel):
    """Odgovor za pročitanu knjigu — uključuje book detalje i datum čitanja."""
    book: BookResponse
    read_at: datetime

    model_config = {"from_attributes": True}
