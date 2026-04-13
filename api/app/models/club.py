# =============================================================
# club.py — Club ORM model
# =============================================================
# Predstavlja knjižni klub u sustavu.
#
# Relacije:
#   Club 1 → N Membership (prijave članova u klub)
#
# Ključni constrainti:
#   - name je UNIQUE: ne smiju postojati dva kluba s istim imenom
#   - max_members > 0: klub mora primati bar jednog člana
#   - registration_deadline: nakon ovog datuma prijave su zatvorene
#
# Dizajnerske odluke:
#   - created_by je FK prema users — admin koji je kreirao klub
#   - min_hours_per_week / pages_per_week: minimalni tempo čitanja
#     koji član mora imati da se prijava ne odbije automatski
# =============================================================

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.book import Book
    from app.models.membership import Membership


class Club(Base):
    """
    Knjižni klub.

    Atributi:
        id:                   Surrogate primary key.
        name:                 Naziv kluba (jedinstven u sustavu).
        description:          Opis kluba (opcionalan).
        max_members:          Maksimalan broj odobrenih članova.
        min_hours_per_week:   Minimalni sati čitanja tjedno za prijavu.
        pages_per_week:       Minimalni broj stranica tjedno za prijavu.
        registration_deadline: Rok do kojeg se može prijaviti (UTC).
        created_by:           FK prema useru koji je kreirao klub (admin).

    Relacije:
        memberships: Lista prijava u ovaj klub.
                     back_populates="club" znači da Membership.club
                     pokazuje natrag na ovaj objekt.
    """



    __tablename__ = "clubs"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    max_members: Mapped[int] = mapped_column(nullable=False)
    min_hours_per_week: Mapped[float] = mapped_column(nullable=False, default=0.0)
    pages_per_week: Mapped[int] = mapped_column(nullable=False, default=0)
    registration_deadline: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    created_by: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    # Trenutna knjiga kluba — nullable, klub možda još nije odabrao
    current_book_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("books.id", ondelete="SET NULL"), nullable=True
    )

    current_book: Mapped[Optional[Book]] = relationship(
        "Book", back_populates="clubs"
    )
    memberships: Mapped[list[Membership]] = relationship(
        "Membership", back_populates="club", cascade="all, delete-orphan"
    )
