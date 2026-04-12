# =============================================================
# membership.py — Membership ORM model
# =============================================================
# Prijava korisnika u knjižni klub.
#
# Ovo je "junction" entitet između User i Club —
# ali nije čista M:N tablica jer ima vlastite atribute
# (status, created_at) i vlastitu poslovnu logiku.
#
# Životni ciklus statusa:
#   pending   → approved  (admin odobri)
#   pending   → rejected  (admin odbije ili automatski pri prijavi)
#   pending   → (deleted) (korisnik povuče prijavu)
#
# Constrainti:
#   - (user_id, club_id) mora biti jedinstven:
#     korisnik se ne može dvaput prijaviti u isti klub
# =============================================================

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.club import Club
    from app.models.user import User


class Membership(Base):
    """
    Prijava korisnika u knjižni klub.

    Atributi:
        id:         Surrogate primary key.
        user_id:    FK prema korisniku koji se prijavio.
        club_id:    FK prema klubu u koji se prijavio.
        status:     "pending" | "approved" | "rejected"
        created_at: Kada je prijava kreirana (automatski, UTC).

    Constrainti:
        uq_memberships_user_club: jedan korisnik, jedan klub — jednom.

    Relacije:
        user: Korisnik koji se prijavio.
        club: Klub u koji se prijavio.
    """

    __tablename__ = "memberships"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    club_id: Mapped[int] = mapped_column(
        ForeignKey("clubs.id", ondelete="CASCADE"), nullable=False
    )

    # Status prijave. String umjesto Enum-a — jednostavnije za početak,
    # validacija u Pydantic schema sloju.
    status: Mapped[str] = mapped_column(
        String(10), nullable=False, default="pending"
    )

    # server_default=func.now() → baza sama postavlja vrijednost pri INSERTu.
    # Bolje od Python-side defaulta jer ne ovisi o server clock-u aplikacije.
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Unique constraint — jedan korisnik se može prijaviti u klub samo jednom.
    # Enforced na razini baze, ne samo u kodu (zaštita od race conditiona).
    __table_args__ = (
        UniqueConstraint("user_id", "club_id", name="uq_memberships_user_club"),
    )

    # ORM relationships
    user: Mapped[User] = relationship(back_populates="memberships")
    club: Mapped[Club] = relationship(back_populates="memberships")
