# =============================================================
# book.py — Book ORM model
# =============================================================
# Knjiga je samostalni entitet koji može biti:
#   - trenutna knjiga kluba (clubs.current_book_id → books.id)
#   - pročitana od strane korisnika (M:N kroz user_books)
# =============================================================

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy import CheckConstraint, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.club import Club
    from app.models.user_book import UserBook


class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    author: Mapped[str] = mapped_column(String(150), nullable=False)
    pages: Mapped[int] = mapped_column(nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Klubovi koji trenutno čitaju ovu knjigu (1:N)
    clubs: Mapped[list[Club]] = relationship("Club", back_populates="current_book")

    # Korisnici koji su pročitali ovu knjigu (M:N)
    user_books: Mapped[list[UserBook]] = relationship(
        "UserBook", back_populates="book", cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint("pages > 0", name="ck_books_pages"),
    )
