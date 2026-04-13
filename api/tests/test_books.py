# =============================================================
# test_books.py — Testovi za book endpointe
# =============================================================
# Pokrivamo:
#   - Katalog: lista i detalji (svi prijavljeni)
#   - Admin CRUD: kreiranje, ažuriranje, brisanje
#   - Role: member ne smije kreirati/brisati
#   - Pročitane knjige: mark/unmark, duplikat zaštita
#   - 401 bez tokena, 403 bez prave role, 404/409
# =============================================================

from httpx import AsyncClient

from tests.conftest import auth_header

# ---- Katalog — lista i detalji ----

async def test_list_books_requires_auth(client: AsyncClient):
    """Bez tokena GET /books vraća 401."""
    resp = await client.get("/books")
    assert resp.status_code == 401


async def test_admin_can_list_books(client: AsyncClient, admin_user, book):
    """Admin vidi katalog knjiga."""
    headers = await auth_header(client, "testadmin", "admin123")
    resp = await client.get("/books", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 1
    assert resp.json()[0]["title"] == "Zločin i kazna"


async def test_member_can_list_books(client: AsyncClient, member_user, book):
    """Member može vidjeti katalog knjiga."""
    headers = await auth_header(client, "testmember", "member123")
    resp = await client.get("/books", headers=headers)
    assert resp.status_code == 200


async def test_get_book_detail(client: AsyncClient, admin_user, book):
    """Detalji knjige po ID-u."""
    headers = await auth_header(client, "testadmin", "admin123")
    resp = await client.get(f"/books/{book.id}", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == "Zločin i kazna"
    assert data["author"] == "Fjodor Dostojevski"
    assert data["pages"] == 624


async def test_get_nonexistent_book(client: AsyncClient, admin_user):
    """Nepostojeća knjiga vraća 404."""
    headers = await auth_header(client, "testadmin", "admin123")
    resp = await client.get("/books/9999", headers=headers)
    assert resp.status_code == 404
    assert resp.json()["code"] == "not_found"


# ---- Admin CRUD ----

async def test_admin_create_book(client: AsyncClient, admin_user):
    """Admin kreira novu knjigu — 201."""
    headers = await auth_header(client, "testadmin", "admin123")
    resp = await client.post(
        "/books",
        json={
            "title": "Majstor i Margarita",
            "author": "Mihail Bulgakov",
            "pages": 480,
            "description": "Satirični roman",
        },
        headers=headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Majstor i Margarita"
    assert data["pages"] == 480


async def test_member_cannot_create_book(client: AsyncClient, member_user):
    """Member ne smije kreirati knjigu — 403."""
    headers = await auth_header(client, "testmember", "member123")
    resp = await client.post(
        "/books",
        json={"title": "Nova knjiga", "author": "Autor", "pages": 100},
        headers=headers,
    )
    assert resp.status_code == 403
    assert resp.json()["code"] == "forbidden"


async def test_admin_update_book(client: AsyncClient, admin_user, book):
    """Admin ažurira podatke knjige."""
    headers = await auth_header(client, "testadmin", "admin123")
    resp = await client.patch(
        f"/books/{book.id}",
        json={"pages": 700, "description": "Ažurirani opis"},
        headers=headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["pages"] == 700
    assert data["description"] == "Ažurirani opis"


async def test_member_cannot_update_book(client: AsyncClient, member_user, book):
    """Member ne smije ažurirati knjigu — 403."""
    headers = await auth_header(client, "testmember", "member123")
    resp = await client.patch(
        f"/books/{book.id}",
        json={"pages": 100},
        headers=headers,
    )
    assert resp.status_code == 403


async def test_admin_delete_book(client: AsyncClient, admin_user, book):
    """Admin briše knjigu — 204."""
    headers = await auth_header(client, "testadmin", "admin123")
    resp = await client.delete(f"/books/{book.id}", headers=headers)
    assert resp.status_code == 204

    # Provjera da knjiga više ne postoji
    resp = await client.get(f"/books/{book.id}", headers=headers)
    assert resp.status_code == 404


async def test_member_cannot_delete_book(client: AsyncClient, member_user, book):
    """Member ne smije brisati knjige — 403."""
    headers = await auth_header(client, "testmember", "member123")
    resp = await client.delete(f"/books/{book.id}", headers=headers)
    assert resp.status_code == 403


# ---- Pročitane knjige ----

async def test_mark_book_as_read(client: AsyncClient, member_user, book):
    """Member označava knjigu kao pročitanu — 201."""
    headers = await auth_header(client, "testmember", "member123")
    resp = await client.post(f"/users/me/books/{book.id}", headers=headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["book"]["id"] == book.id
    assert "read_at" in data


async def test_mark_book_already_read(client: AsyncClient, member_user, book):
    """Duplikat označavanja vraća 409."""
    headers = await auth_header(client, "testmember", "member123")
    await client.post(f"/users/me/books/{book.id}", headers=headers)
    resp = await client.post(f"/users/me/books/{book.id}", headers=headers)
    assert resp.status_code == 409
    assert resp.json()["code"] == "already_read"


async def test_get_my_books(client: AsyncClient, member_user, book):
    """Korisnik vidi svoje pročitane knjige."""
    headers = await auth_header(client, "testmember", "member123")
    await client.post(f"/users/me/books/{book.id}", headers=headers)

    resp = await client.get("/users/me/books", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 1
    assert resp.json()[0]["book"]["title"] == "Zločin i kazna"


async def test_unmark_book_as_read(client: AsyncClient, member_user, book):
    """Korisnik uklanja oznaku pročitane knjige — 204."""
    headers = await auth_header(client, "testmember", "member123")
    await client.post(f"/users/me/books/{book.id}", headers=headers)

    resp = await client.delete(f"/users/me/books/{book.id}", headers=headers)
    assert resp.status_code == 204

    # Lista je sada prazna
    resp = await client.get("/users/me/books", headers=headers)
    assert resp.json() == []


async def test_unmark_book_not_read(client: AsyncClient, member_user, book):
    """Uklanjanje oznake za nepročitanu knjigu vraća 404."""
    headers = await auth_header(client, "testmember", "member123")
    resp = await client.delete(f"/users/me/books/{book.id}", headers=headers)
    assert resp.status_code == 404
    assert resp.json()["code"] == "not_found"


async def test_mark_nonexistent_book(client: AsyncClient, member_user):
    """Označavanje nepostojeće knjige vraća 404."""
    headers = await auth_header(client, "testmember", "member123")
    resp = await client.post("/users/me/books/9999", headers=headers)
    assert resp.status_code == 404
