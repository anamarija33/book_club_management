from datetime import datetime, timedelta, timezone
from typing import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.core.database import Base
from app.core.deps import get_db
from app.core.security import hash_password
from app.main import app as fastapi_app
from app.models.book import Book
from app.models.club import Club
from app.models.user import User

engine_test = create_async_engine(
    "sqlite+aiosqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestSessionLocal = async_sessionmaker(
    bind=engine_test, class_=AsyncSession, expire_on_commit=False
)


async def _override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with TestSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


fastapi_app.dependency_overrides[get_db] = _override_get_db


def _future_deadline(days: int = 30) -> datetime:
    return datetime.now(timezone.utc) + timedelta(days=days)


@pytest.fixture(autouse=True)
async def setup_database():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def db() -> AsyncGenerator[AsyncSession, None]:
    async with TestSessionLocal() as session:
        yield session


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=fastapi_app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def admin_user(db: AsyncSession) -> User:
    user = User(
        username="testadmin",
        email="admin@test.local",
        password_hash=hash_password("admin123"),
        role="admin",
        is_active=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest.fixture
async def member_user(db: AsyncSession) -> User:
    user = User(
        username="testmember",
        email="member@test.local",
        password_hash=hash_password("member123"),
        role="member",
        is_active=True,
        hours_per_week=3.0,
        pages_per_week=50,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest.fixture
async def club_and_member(db: AsyncSession, admin_user: User) -> tuple[Club, User]:
    club = Club(
        name="Čitači klasika",
        description="Klub za ljubitelje klasike",
        max_members=20,
        min_hours_per_week=2.0,
        pages_per_week=30,
        registration_deadline=_future_deadline(30),
        created_by=admin_user.id,
    )
    db.add(club)
    await db.flush()

    member = User(
        username="testmember",
        email="member@test.local",
        password_hash=hash_password("member123"),
        role="member",
        is_active=True,
        hours_per_week=3.0,
        pages_per_week=50,
    )
    db.add(member)
    await db.commit()
    await db.refresh(member)
    await db.refresh(club)
    return club, member


@pytest.fixture
async def club_b(db: AsyncSession, admin_user: User) -> Club:
    club = Club(
        name="Sci-Fi entuzijasti",
        description="Za ljubitelje SF-a",
        max_members=15,
        min_hours_per_week=1.0,
        pages_per_week=20,
        registration_deadline=_future_deadline(30),
        created_by=admin_user.id,
    )
    db.add(club)
    await db.commit()
    await db.refresh(club)
    return club


@pytest.fixture
async def inactive_user(db: AsyncSession) -> User:
    user = User(
        username="inactive",
        email="inactive@test.local",
        password_hash=hash_password("pass123"),
        role="member",
        is_active=False,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest.fixture
async def book(db: AsyncSession) -> Book:
    """Demo knjiga za testove."""
    b = Book(
        title="Zločin i kazna",
        author="Fjodor Dostojevski",
        pages=624,
        description="Klasik ruske književnosti",
    )
    db.add(b)
    await db.commit()
    await db.refresh(b)
    return b


async def auth_header(client: AsyncClient, username: str, password: str) -> dict:
    resp = await client.post(
        "/auth/login", json={"username": username, "password": password}
    )
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
