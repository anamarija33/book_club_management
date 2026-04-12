# =============================================================
# seed.py — Inicijalni podaci za razvoj i testiranje
# =============================================================
# Kreira admin korisnika i dva demo kluba s njihovim članovima.
#
# Pokretanje (iz api/ direktorija):
#   python -m app.seed
#
# Zašto seed?
#   - Nakon "alembic upgrade head" imamo prazne tablice
#   - Za razvoj trebamo barem admin login i klubove
#   - Za testiranje auth/ownership logike (predavanje 3)
#     trebamo dva kluba da dokažemo isolation između članova
#
# Idempotentnost:
#   Skripta provjerava postoji li već zapis s istim username/imenom.
#   Ako postoji — preskače. Sigurno je pokrenuti višestruko.
# =============================================================

import asyncio
import logging
from datetime import datetime, timedelta, timezone

import bcrypt as _bcrypt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal, engine
from app.models.club import Club
from app.models.user import User

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---- Seed podaci ------------------------------------------------
ADMIN_USERNAME = "admin"
ADMIN_EMAIL = "admin@bookclub.com"
ADMIN_PASSWORD = "admin123"

# Dva demo kluba — za testiranje da jedan admin ne vidi drugog
CLUBS = [
    {
        "name": "Čitači klasika",
        "description": "Klub posvećen klasičnoj književnosti",
        "max_members": 20,
        "min_hours_per_week": 3.0,
        "pages_per_week": 50,
        # Korisnik koji pripada ovom klubu (za testiranje membership logike)
        "member_username": "marko",
        "member_email": "marko@bookclub.local",
        "member_password": "marko123",
        "member_hours": 4.0,
        "member_pages": 60,
    },
    {
        "name": "Sci-Fi entuzijasti",
        "description": "Klub za ljubitelje znanstvene fantastike",
        "max_members": 15,
        "min_hours_per_week": 2.0,
        "pages_per_week": 40,
        "member_username": "ana",
        "member_email": "ana@bookclub.local",
        "member_password": "ana123",
        "member_hours": 5.0,
        "member_pages": 80,
    },
]


def _hash_pw(plain: str) -> str:
    return _bcrypt.hashpw(plain.encode(), _bcrypt.gensalt()).decode()


async def _seed_admin(session: AsyncSession) -> User:
    """Kreiraj admin korisnika ako ne postoji."""
    result = await session.execute(
        select(User).where(User.username == ADMIN_USERNAME)
    )
    admin = result.scalar_one_or_none()

    if admin is None:
        admin = User(
            username=ADMIN_USERNAME,
            email=ADMIN_EMAIL,
            password_hash=_hash_pw(ADMIN_PASSWORD),
            role="admin",
        )
        session.add(admin)
        await session.flush()  # flush da dobijemo admin.id prije kreiranja klubova
        logger.info("Kreiran admin: %s (id=%s)", admin.username, admin.id)
    else:
        logger.info("Admin '%s' već postoji - preskačem.", admin.username)

    return admin


async def _seed_club(session: AsyncSession, data: dict, admin_id: int) -> None:
    """Kreiraj klub i člana ako ne postoje."""

    result = await session.execute(select(Club).where(Club.name == data["name"]))
    club = result.scalar_one_or_none()

    if club is None:
        club = Club(
            name=data["name"],
            description=data.get("description"),
            max_members=data["max_members"],
            min_hours_per_week=data["min_hours_per_week"],
            pages_per_week=data["pages_per_week"],
            # Rok za prijavu: 30 dana od danas
            registration_deadline=datetime.now(timezone.utc) + timedelta(days=30),
            created_by=admin_id,
        )
        session.add(club)
        await session.flush()
        logger.info("Kreiran klub: %s (id=%s)", club.name, club.id)
    else:
        logger.info("Klub '%s' već postoji — preskačem.", club.name)


    result = await session.execute(
        select(User).where(User.username == data["member_username"])
    )
    if result.scalar_one_or_none() is None:
        member = User(
            username=data["member_username"],
            email=data["member_email"],
            password_hash=_hash_pw(data["member_password"]),
            role="member",
            hours_per_week=data["member_hours"],
            pages_per_week=data["member_pages"],
        )
        session.add(member)
        logger.info(
            "Kreiran member: %s (hours=%.1f, pages=%d)",
            member.username,
            member.hours_per_week,
            member.pages_per_week,
        )


async def seed(session: AsyncSession) -> None:
    """
    Kreira inicijalne podatke ako ne postoje.

    Redoslijed je bitan:
      1. Admin prvi (jer klub treba created_by = admin.id)
      2. Klubovi + njihovi članovi
    """
    admin = await _seed_admin(session)

    for club_data in CLUBS:
        await _seed_club(session, club_data, admin.id)

    await session.commit()
    logger.info("Seed završen uspješno!")


async def main() -> None:
    """Entry point — otvara sesiju, pokreće seed, zatvara engine."""
    async with AsyncSessionLocal() as session:
        await seed(session)
    # Čisto zatvaranje svih konekcija u poolu.
    await engine.dispose()


# Omogućuje pokretanje sa: python -m app.seed
if __name__ == "__main__":
    asyncio.run(main())
