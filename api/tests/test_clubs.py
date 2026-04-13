# =============================================================
# test_clubs.py — Testovi za autorizaciju i ownership na club endpointima
# =============================================================
# Pokrivamo:
#   - Role testovi: member ne smije kreirati/brisati/mijenjati klub
#   - Ownership: admin vidi sve, member vidi sve (membership logika dolazi)
#   - Admin CRUD: kreiranje, ažuriranje, brisanje
#   - 401 bez tokena, 403 bez prave role, 404 za nepostojeći klub
# =============================================================

from datetime import datetime, timedelta, timezone

import pytest
from httpx import AsyncClient

from tests.conftest import auth_header


def _future_deadline(days: int = 30) -> str:
    """ISO8601 datetime 'days' dana u budućnosti."""
    return (datetime.now(timezone.utc) + timedelta(days=days)).isoformat()


# ---- Role testovi ------------------------------------------------

async def test_member_cannot_create_club(client: AsyncClient, club_and_member):
    """Member ne smije kreirati novi klub (403)."""
    _, member = club_and_member
    headers = await auth_header(client, "testmember", "member123")
    resp = await client.post(
        "/clubs/",
        json={
            "name": "Novi klub",
            "max_members": 10,
            "min_hours_per_week": 1.0,
            "pages_per_week": 20,
            "registration_deadline": _future_deadline(),
        },
        headers=headers,
    )
    assert resp.status_code == 403
    assert resp.json()["code"] == "forbidden"


async def test_admin_can_create_club(client: AsyncClient, admin_user):
    """Admin kreira klub — vraća 201 s ispravnim podacima."""
    headers = await auth_header(client, "testadmin", "admin123")
    resp = await client.post(
        "/clubs/",
        json={
            "name": "Novi knjižni klub",
            "description": "Opis kluba",
            "max_members": 15,
            "min_hours_per_week": 2.0,
            "pages_per_week": 40,
            "registration_deadline": _future_deadline(),
        },
        headers=headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Novi knjižni klub"
    assert data["max_members"] == 15
    assert data["created_by"] == admin_user.id


async def test_member_cannot_update_club(client: AsyncClient, club_and_member):
    """Member ne smije PATCH-irati klub (admin-only, 403)."""
    club, _ = club_and_member
    headers = await auth_header(client, "testmember", "member123")
    resp = await client.patch(
        f"/clubs/{club.id}",
        json={"max_members": 5},
        headers=headers,
    )
    assert resp.status_code == 403


async def test_member_cannot_delete_club(client: AsyncClient, club_and_member):
    """Member ne smije obrisati klub (admin-only, 403)."""
    club, _ = club_and_member
    headers = await auth_header(client, "testmember", "member123")
    resp = await client.delete(f"/clubs/{club.id}", headers=headers)
    assert resp.status_code == 403


async def test_unauthenticated_cannot_access_clubs(client: AsyncClient):
    """Bez tokena GET /clubs vraća 401."""
    resp = await client.get("/clubs/")
    assert resp.status_code == 401


# ---- Listing testovi ---------------------------------------------

async def test_admin_sees_all_clubs(
    client: AsyncClient, admin_user, club_and_member, club_b
):
    """Admin vidi sve klubove u listi."""
    headers = await auth_header(client, "testadmin", "admin123")
    resp = await client.get("/clubs/", headers=headers)

    assert resp.status_code == 200
    assert len(resp.json()) == 2


async def test_member_sees_clubs(client: AsyncClient, club_and_member, club_b):
    """Member može vidjeti listu klubova."""
    _, member = club_and_member
    headers = await auth_header(client, "testmember", "member123")
    resp = await client.get("/clubs/", headers=headers)

    assert resp.status_code == 200


# ---- Detalji kluba -----------------------------------------------

async def test_admin_can_see_any_club(client: AsyncClient, admin_user, club_and_member):
    """Admin može vidjeti detalje bilo kojeg kluba."""
    club, _ = club_and_member
    headers = await auth_header(client, "testadmin", "admin123")
    resp = await client.get(f"/clubs/{club.id}", headers=headers)

    assert resp.status_code == 200
    assert resp.json()["name"] == "Čitači klasika"


async def test_member_can_see_club_details(client: AsyncClient, club_and_member):
    """Member može vidjeti detalje kluba."""
    club, _ = club_and_member
    headers = await auth_header(client, "testmember", "member123")
    resp = await client.get(f"/clubs/{club.id}", headers=headers)

    assert resp.status_code == 200


async def test_get_nonexistent_club(client: AsyncClient, admin_user):
    """Dohvat nepostojećeg kluba vraća 404."""
    headers = await auth_header(client, "testadmin", "admin123")
    resp = await client.get("/clubs/9999", headers=headers)
    assert resp.status_code == 404
    assert resp.json()["code"] == "not_found"


# ---- Admin CRUD testovi ------------------------------------------

async def test_admin_update_club(client: AsyncClient, admin_user, club_and_member):
    """Admin može ažurirati podatke kluba."""
    club, _ = club_and_member
    headers = await auth_header(client, "testadmin", "admin123")
    resp = await client.patch(
        f"/clubs/{club.id}",
        json={"max_members": 25, "description": "Ažurirani opis"},
        headers=headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["max_members"] == 25
    assert data["description"] == "Ažurirani opis"


async def test_admin_delete_club(client: AsyncClient, admin_user, club_and_member):
    """Admin može obrisati klub."""
    club, _ = club_and_member
    headers = await auth_header(client, "testadmin", "admin123")
    resp = await client.delete(f"/clubs/{club.id}", headers=headers)
    assert resp.status_code == 204

    # Provjera da klub više ne postoji
    resp = await client.get(f"/clubs/{club.id}", headers=headers)
    assert resp.status_code == 404


async def test_create_duplicate_club(client: AsyncClient, admin_user, club_and_member):
    """Kreiranje kluba s postojećim imenom vraća 409."""
    headers = await auth_header(client, "testadmin", "admin123")
    resp = await client.post(
        "/clubs/",
        json={
            "name": "Čitači klasika",  # već postoji
            "max_members": 10,
            "min_hours_per_week": 1.0,
            "pages_per_week": 20,
            "registration_deadline": _future_deadline(),
        },
        headers=headers,
    )
    assert resp.status_code == 409
    assert resp.json()["code"] == "duplicate"
