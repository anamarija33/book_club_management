# =============================================================
# schemas/auth.py — Pydantic scheme za autentikaciju
# =============================================================
# Schema = ugovor API-ja. Definira što prima i što vraća endpoint.
#
# LoginRequest  → tijelo POST /auth/login
# TokenResponse → odgovor s JWT tokenima
# RefreshRequest → tijelo POST /auth/refresh
# UserResponse  → odgovor GET /auth/me (bez password_hash!)
# =============================================================

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """Tijelo POST /auth/login requesta."""
    username: str = Field(min_length=1, max_length=50)
    password: str = Field(min_length=1)


class TokenResponse(BaseModel):
    """Odgovor s JWT tokenima nakon uspješnog logina ili refresha."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    """Tijelo POST /auth/refresh requesta."""
    refresh_token: str


class UserResponse(BaseModel):
    """
    Prikaz trenutnog korisnika (GET /auth/me).
    Nikad ne vraćamo password_hash — model vs schema razlika.
    """
    id: int
    username: str
    email: str
    role: str
    is_active: bool
    hours_per_week: float
    pages_per_week: int

    model_config = {"from_attributes": True}
