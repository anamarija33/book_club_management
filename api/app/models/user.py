# =============================================================
# user.py — User ORM model
# =============================================================
# Korisnik sustava — može biti admin ili member.
#
# Role:
#   "admin"  — upravlja klubovima, odobrava/odbija prijave
#   "member" — prijavljuje se u knjišve klubove
#
# Dizajnerske odluke:
#   - role je String (ne Enum) — jednostavnije za početak,
#     validacija se radi u Pydantic schema sloju
#   - username je UNIQUE: sprječava duplicirane loginove
#   - email je UNIQUE: jedan email = jedan račun
#   - password_hash: NIKAD ne spremamo lozinku u čistom tekstu!
#   - is_active: omogućuje deaktivaciju korisnika bez brisanja
#   - hours_per_week / pages_per_week: tempo čitanja korisnika,
#     uspoređuje se s minimalnim tempom kluba pri prijavi
# =============================================================

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.membership import Membership


class User(Base):
    """
    Korisnik sustava (admin ili member).

    Atributi:
        id:             Surrogate primary key.
        username:       Login korisničko ime (jedinstven u sustavu).
        email:          Email adresa (jedinstvena u sustavu).
        password_hash:  Bcrypt hash lozinke (NIKAD plain text).
        role:           "admin" ili "member".
        is_active:      Može li se korisnik prijaviti.
        hours_per_week: Koliko sati tjedno korisnik čita.
        pages_per_week: Koliko stranica tjedno korisnik čita.

    Relacije:
        memberships: Lista prijava korisnika u knjišve klubove.
                     back_populates="user" znači da Membership.user
                     pokazuje natrag na ovaj objekt.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="member")
    is_active: Mapped[bool] = mapped_column(default=True)

    # Tempo čitanja — uspoređuje se s minimalnim tempom kluba pri prijavi.
    # Ako korisnik ne zadovoljava uvjete, prijava se automatski odbija.
    hours_per_week: Mapped[float] = mapped_column(nullable=False, default=0.0)
    pages_per_week: Mapped[int] = mapped_column(nullable=False, default=0)

    # ORM relationship — omogućuje user.memberships umjesto ručnog querya.
    memberships: Mapped[list[Membership]] = relationship(back_populates="user")
