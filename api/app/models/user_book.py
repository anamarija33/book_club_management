# =============================================================
# user_book.py — M:N tablica: users <-> books
# =============================================================
# Prati koje knjige je korisnik pročitao i kada.
# Ima vlastiti atribut read_at — nije čista asocijacijska tablica
# nego punopravni ORM model.
#
# Kompozitni primarni ključ (user_id, book_id) osigurava
# da korisnik može označiti knjigu kao pročitanu samo jednom.
# =============================================================

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.book import Book
    from app.models.user import User


class UserBook(Base):
    __tablename__ = "user_books"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    book_id: Mapped[int] = mapped_column(
        ForeignKey("books.id", ondelete="CASCADE"), primary_key=True
    )
    read_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    user: Mapped[User] = relationship("User", back_populates="user_books")
    book: Mapped[Book] = relationship("Book", back_populates="user_books")
