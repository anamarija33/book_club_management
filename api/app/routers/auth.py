# =============================================================
# routers/auth.py — Autentikacijski endpointi (3)
# =============================================================
# POST /auth/login   — prijava, vraća access + refresh token
# POST /auth/refresh — obnavljanje access tokena
# GET  /auth/me      — podatci o prijavljenom korisniku
#
# Router je tanak — samo parsira request, poziva service,
# mapira rezultat u response. Nikakve poslovne logike ovdje.
# =============================================================

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, RefreshRequest, TokenResponse, UserResponse
from app.services import auth_service

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Autenticiraj korisnika i vrati JWT tokene."""
    user = await auth_service.authenticate_user(db, body.username, body.password)
    access, refresh = auth_service.create_tokens(user)
    return TokenResponse(access_token=access, refresh_token=refresh)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(body: RefreshRequest, db: AsyncSession = Depends(get_db)):
    """Obnovi access token koristeći valjan refresh token."""
    access, refresh_tok = await auth_service.refresh_tokens(db, body.refresh_token)
    return TokenResponse(access_token=access, refresh_token=refresh_tok)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Vrati podatke o trenutno prijavljenom korisniku."""
    return current_user
