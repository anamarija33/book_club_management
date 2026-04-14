# =============================================================
# routers/memberships.py — Membership endpointi
# =============================================================
# GET    /clubs/{club_id}/memberships          — lista prijava
# POST   /clubs/{club_id}/memberships          — prijavi se
# PATCH  /clubs/{club_id}/memberships/{id}     — odobri/odbij (admin)
# DELETE /clubs/{club_id}/memberships/{id}     — povuci prijavu
# =============================================================

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_db, require_role
from app.models.user import User
from app.schemas.membership import MembershipResponse, MembershipStatusUpdate
from app.services import membership_service

router = APIRouter()


@router.get("/", response_model=list[MembershipResponse])
async def list_memberships(
    club_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "member")),
):
    """Admin vidi sve prijave, member vidi samo svoju."""
    memberships = await membership_service.list_memberships(db, club_id, current_user)
    return [MembershipResponse.from_membership(m) for m in memberships]


@router.post(
    "/",
    response_model=MembershipResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_membership(
    club_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("member")),
):
    """Member se prijavljuje u knjižni klub."""
    membership = await membership_service.create_membership(db, club_id, current_user)
    return MembershipResponse.from_membership(membership)


@router.patch("/{membership_id}", response_model=MembershipResponse)
async def update_membership(
    club_id: int,
    membership_id: int,
    body: MembershipStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    """Admin odobrava ili odbija prijavu."""
    membership = await membership_service.update_membership_status(
        db, club_id, membership_id, body.status, current_user
    )
    return MembershipResponse.from_membership(membership)


@router.delete("/{membership_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_membership(
    club_id: int,
    membership_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin", "member")),
):
    """Member povlači svoju pending prijavu, admin briše bilo koju."""
    await membership_service.delete_membership(
        db, club_id, membership_id, current_user
    )
