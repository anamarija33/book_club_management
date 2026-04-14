# =============================================================
# test_memberships.py — Testovi za membership endpointe
# =============================================================

from datetime import datetime, timedelta, timezone

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.club import Club
from app.models.user import User
from tests.conftest import auth_header


# ---- Prijava u klub ----

async def test_member_can_join_club(client: AsyncClient, club_and_member):
    """Member se uspješno prijavljuje u klub."""
    club, member = club_and_member
    headers = await auth_header(client, "testmember", "member123")
    resp = await client.post(f"/clubs/{club.id}/memberships/", headers=headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["status"] == "pending"
    assert data["club_id"] == club.id
    assert data["username"] == "testmember"


async def test_member_cannot_join_twice(client: AsyncClient, club_and_member):
    """Dupla prijava vraća 409."""
    club, _ = club_and_member
    headers = await auth_header(client, "testmember", "member123")
    await client.post(f"/clubs/{club.id}/memberships/", headers=headers)
    resp = await client.post(f"/clubs/{club.id}/memberships/", headers=headers)
    assert resp.status_code == 409
    assert resp.json()["code"] == "already_member"


async def test_admin_cannot_join_club(client: AsyncClient, club_and_member):
    """Admin ne može biti member kluba — 403."""
    club, _ = club_and_member
    headers = await auth_header(client, "testadmin", "admin123")
    resp = await client.post(f"/clubs/{club.id}/memberships/", headers=headers)
    assert resp.status_code == 403


async def test_cannot_join_after_deadline(
    client: AsyncClient, admin_user: User, db: AsyncSession
):
    """Prijava nakon roka vraća 400."""
    past_deadline = datetime.now(timezone.utc) - timedelta(days=1)
    club = Club(
        name="Stari klub",
        max_members=10,
        min_hours_per_week=1.0,
        pages_per_week=10,
        registration_deadline=past_deadline,
        created_by=admin_user.id,
    )
    db.add(club)

    member = User(
        username="latemember",
        email="late@test.local",
        password_hash="x",
        role="member",
    )
    db.add(member)
    await db.commit()
    await db.refresh(club)

    from app.core.security import hash_password
    member.password_hash = hash_password("late123")
    await db.commit()

    headers = await auth_header(client, "latemember", "late123")
    resp = await client.post(f"/clubs/{club.id}/memberships/", headers=headers)
    assert resp.status_code == 400
    assert resp.json()["code"] == "deadline_passed"


# ---- Admin odobrava / odbija ----

async def test_admin_can_approve_membership(client: AsyncClient, club_and_member):
    """Admin odobrava prijavu — status postaje approved."""
    club, _ = club_and_member
    member_headers = await auth_header(client, "testmember", "member123")
    resp = await client.post(f"/clubs/{club.id}/memberships/", headers=member_headers)
    membership_id = resp.json()["id"]

    admin_headers = await auth_header(client, "testadmin", "admin123")
    resp = await client.patch(
        f"/clubs/{club.id}/memberships/{membership_id}",
        json={"status": "approved"},
        headers=admin_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "approved"


async def test_admin_can_reject_membership(client: AsyncClient, club_and_member):
    """Admin odbija prijavu — status postaje rejected."""
    club, _ = club_and_member
    member_headers = await auth_header(client, "testmember", "member123")
    resp = await client.post(f"/clubs/{club.id}/memberships/", headers=member_headers)
    membership_id = resp.json()["id"]

    admin_headers = await auth_header(client, "testadmin", "admin123")
    resp = await client.patch(
        f"/clubs/{club.id}/memberships/{membership_id}",
        json={"status": "rejected"},
        headers=admin_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "rejected"


async def test_member_cannot_approve(client: AsyncClient, club_and_member):
    """Member ne smije odobravati prijave — 403."""
    club, _ = club_and_member
    headers = await auth_header(client, "testmember", "member123")
    resp = await client.post(f"/clubs/{club.id}/memberships/", headers=headers)
    membership_id = resp.json()["id"]

    resp = await client.patch(
        f"/clubs/{club.id}/memberships/{membership_id}",
        json={"status": "approved"},
        headers=headers,
    )
    assert resp.status_code == 403


# ---- Listanje ----

async def test_admin_sees_all_memberships(client: AsyncClient, club_and_member):
    """Admin vidi sve prijave za klub."""
    club, _ = club_and_member
    member_headers = await auth_header(client, "testmember", "member123")
    await client.post(f"/clubs/{club.id}/memberships/", headers=member_headers)

    admin_headers = await auth_header(client, "testadmin", "admin123")
    resp = await client.get(f"/clubs/{club.id}/memberships/", headers=admin_headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 1


async def test_member_sees_own_membership(client: AsyncClient, club_and_member):
    """Member vidi samo svoju prijavu."""
    club, _ = club_and_member
    headers = await auth_header(client, "testmember", "member123")
    await client.post(f"/clubs/{club.id}/memberships/", headers=headers)

    resp = await client.get(f"/clubs/{club.id}/memberships/", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 1
    assert resp.json()[0]["user_id"] is not None


# ---- Brisanje ----

async def test_member_can_withdraw_pending(client: AsyncClient, club_and_member):
    """Member povlači pending prijavu — 204."""
    club, _ = club_and_member
    headers = await auth_header(client, "testmember", "member123")
    resp = await client.post(f"/clubs/{club.id}/memberships/", headers=headers)
    membership_id = resp.json()["id"]

    resp = await client.delete(
        f"/clubs/{club.id}/memberships/{membership_id}", headers=headers
    )
    assert resp.status_code == 204


async def test_member_cannot_withdraw_approved(client: AsyncClient, club_and_member):
    """Member ne može povući approved prijavu — 400."""
    club, _ = club_and_member
    member_headers = await auth_header(client, "testmember", "member123")
    resp = await client.post(f"/clubs/{club.id}/memberships/", headers=member_headers)
    membership_id = resp.json()["id"]

    admin_headers = await auth_header(client, "testadmin", "admin123")
    await client.patch(
        f"/clubs/{club.id}/memberships/{membership_id}",
        json={"status": "approved"},
        headers=admin_headers,
    )

    resp = await client.delete(
        f"/clubs/{club.id}/memberships/{membership_id}", headers=member_headers
    )
    assert resp.status_code == 400
    assert resp.json()["code"] == "invalid_status"


async def test_join_full_club(
    client: AsyncClient, admin_user: User, db: AsyncSession
):
    """Prijava u pun klub vraća 409."""
    club = Club(
        name="Mali klub",
        max_members=1,
        min_hours_per_week=1.0,
        pages_per_week=10,
        registration_deadline=datetime.now(timezone.utc) + timedelta(days=30),
        created_by=admin_user.id,
    )
    db.add(club)

    from app.core.security import hash_password
    m1 = User(
        username="member1", email="m1@test.local",
        password_hash=hash_password("pass1"), role="member",
    )
    m2 = User(
        username="member2", email="m2@test.local",
        password_hash=hash_password("pass2"), role="member",
    )
    db.add(m1)
    db.add(m2)
    await db.commit()
    await db.refresh(club)

    # m1 se prijavi i bude odobren
    h1 = await auth_header(client, "member1", "pass1")
    resp = await client.post(f"/clubs/{club.id}/memberships/", headers=h1)
    mid = resp.json()["id"]
    admin_h = await auth_header(client, "testadmin", "admin123")
    await client.patch(
        f"/clubs/{club.id}/memberships/{mid}",
        json={"status": "approved"}, headers=admin_h,
    )

    # m2 pokuša ući u puni klub
    h2 = await auth_header(client, "member2", "pass2")
    resp = await client.post(f"/clubs/{club.id}/memberships/", headers=h2)
    assert resp.status_code == 409
    assert resp.json()["code"] == "club_full"
