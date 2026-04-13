import asyncio
import logging

import bcrypt as _bcrypt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal, engine
from app.models.club import Club
from app.models.user import User

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ADMIN_USERNAME = "admin"
ADMIN_EMAIL = "admin@bookclub.local"
ADMIN_PASSWORD = "admin123"

CLUBS = [
    {
        "name": "Čitači klasika",
        "description": "Klub posvećen klasičnoj književnosti",
        "max_members": 20,
        "min_hours_per_week": 3.0,
        "pages_per_week": 50,
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
        await session.flush()
        logger.info("Kreiran admin: %s (id=%s)", admin.username, admin.id)
    else:
        logger.info("Admin '%s' vec postoji.", admin.username)

    return admin


async def _seed_club(session: AsyncSession, data: dict, admin_id: int) -> None:
    from datetime import datetime, timedelta, timezone

    result = await session.execute(select(Club).where(Club.name == data["name"]))
    club = result.scalar_one_or_none()

    if club is None:
        club = Club(
            name=data["name"],
            description=data.get("description"),
            max_members=data["max_members"],
            min_hours_per_week=data["min_hours_per_week"],
            pages_per_week=data["pages_per_week"],
            registration_deadline=datetime.now(timezone.utc) + timedelta(days=30),
            created_by=admin_id,
        )
        session.add(club)
        await session.flush()
        logger.info("Kreiran klub: %s (id=%s)", club.name, club.id)
    else:
        logger.info("Klub '%s' vec postoji.", club.name)

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
        logger.info("Kreiran member: %s", member.username)


async def seed(session: AsyncSession) -> None:
    admin = await _seed_admin(session)
    for club_data in CLUBS:
        await _seed_club(session, club_data, admin.id)
    await session.commit()
    logger.info("Seed zavrsen!")
    logger.info("Admin:  username=admin   password=admin123")
    logger.info("Member: username=marko   password=marko123")
    logger.info("Member: username=ana     password=ana123")


async def main() -> None:
    async with AsyncSessionLocal() as session:
        await seed(session)
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())