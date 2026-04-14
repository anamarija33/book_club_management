# =============================================================
# schemas/membership.py — Pydantic scheme za Membership entitet
# =============================================================

from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class MembershipCreate(BaseModel):
    """POST /clubs/{club_id}/memberships — member se prijavljuje."""
    pass  # Nema body — sve se čita iz tokena (user_id) i URL-a (club_id)


class MembershipStatusUpdate(BaseModel):
    """PATCH /clubs/{club_id}/memberships/{id} — admin mijenja status."""
    status: Literal["approved", "rejected"]


class MembershipResponse(BaseModel):
    id: int
    user_id: int
    club_id: int
    status: str
    created_at: datetime
    username: str | None = None  # iz user relacije

    model_config = {"from_attributes": True}

    @classmethod
    def from_membership(cls, m) -> "MembershipResponse":
        return cls(
            id=m.id,
            user_id=m.user_id,
            club_id=m.club_id,
            status=m.status,
            created_at=m.created_at,
            username=m.user.username if m.user else None,
        )
