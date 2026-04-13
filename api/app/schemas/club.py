# =============================================================
# schemas/club.py — Pydantic scheme za Club entitet
# =============================================================
# ClubCreate   — što admin šalje kad kreira klub
# ClubUpdate   — parcijalni update (sva polja opcionalna)
# ClubResponse — što API vraća
# =============================================================

from datetime import datetime

from pydantic import BaseModel, Field


class ClubCreate(BaseModel):
    """POST /clubs — admin kreira knjižni klub."""
    name: str = Field(min_length=1, max_length=120)
    description: str | None = None
    max_members: int = Field(gt=0)
    min_hours_per_week: float = Field(ge=0.0)
    pages_per_week: int = Field(ge=0)
    registration_deadline: datetime


class ClubUpdate(BaseModel):
    """PATCH /clubs/{id} — parcijalni update (samo poslana polja se mijenjaju)."""
    name: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = None
    max_members: int | None = Field(default=None, gt=0)
    min_hours_per_week: float | None = Field(default=None, ge=0.0)
    pages_per_week: int | None = Field(default=None, ge=0)
    registration_deadline: datetime | None = None


class ClubResponse(BaseModel):
    """Odgovor s podacima o klubu."""
    id: int
    name: str
    description: str | None = None
    max_members: int
    min_hours_per_week: float
    pages_per_week: int
    registration_deadline: datetime
    created_by: int

    model_config = {"from_attributes": True}
