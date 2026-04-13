# =============================================================
# routers/clubs.py — Club endpointi
# =============================================================
# GET    /clubs/          — lista klubova (admin + member)
# POST   /clubs/          — kreiraj klub (admin only)
# GET    /clubs/{id}      — detalji kluba (admin + member)
# PATCH  /clubs/{id}      — ažuriraj klub (admin only)
# DELETE /clubs/{id}      — obriši klub (admin only)
#
# require_role("admin") → 403 ako nije admin
# require_role("admin", "member") → 403 ako nije ni jedno
#
# 401 = nisi prijavljen
# 403 = prijavljen si, ali nemaš pravo
# =============================================================

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db, require_role
from app.models.user import User
from app.schemas.club import ClubCreate, ClubResponse, ClubUpdate
from app.services import club_service

router = APIRouter()


@router.get("/", response_model=list[ClubResponse])
async def list_clubs(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("admin", "member")),
):
    """Lista svih klubova. Admin vidi sve, member vidi sve (ownership na memberships)."""
    clubs = await club_service.list_clubs(db, user)
    return clubs


@router.post("/", response_model=ClubResponse, status_code=status.HTTP_201_CREATED)
async def create_club(
    body: ClubCreate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_role("admin")),
):
    """Admin kreira novi knjižni klub."""
    club = await club_service.create_club(
        db,
        name=body.name,
        description=body.description,
        max_members=body.max_members,
        min_hours_per_week=body.min_hours_per_week,
        pages_per_week=body.pages_per_week,
        registration_deadline=body.registration_deadline,
        admin_id=admin.id,
    )
    return club


@router.get("/{club_id}", response_model=ClubResponse)
async def get_club(
    club_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("admin", "member")),
):
    """Detalji kluba."""
    club = await club_service.get_club(db, club_id, user)
    return club


@router.patch("/{club_id}", response_model=ClubResponse)
async def update_club(
    club_id: int,
    body: ClubUpdate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_role("admin")),
):
    """Admin ažurira podatke kluba (parcijalni update)."""
    club = await club_service.update_club(
        db,
        club_id=club_id,
        current_user=admin,
        name=body.name,
        description=body.description,
        max_members=body.max_members,
        min_hours_per_week=body.min_hours_per_week,
        pages_per_week=body.pages_per_week,
        registration_deadline=body.registration_deadline,
    )
    return club


@router.delete("/{club_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_club(
    club_id: int,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(require_role("admin")),
):
    """Admin briše klub."""
    await club_service.delete_club(db, club_id)
