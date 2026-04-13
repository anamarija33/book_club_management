# =============================================================
# deps.py — Zajedničke FastAPI dependencije
# =============================================================
# FastAPI koristi Dependency Injection (DI) sustav:
# endpoint deklarira ŠTO treba, a framework KAKO to dobiti.
#
# Primjer (dolazi u predavanju 2-3):
#   async def get_db() -> AsyncGenerator[AsyncSession, None]:
#       async with SessionLocal() as session:
#           yield session
#
#   @router.get("/lifters")
#   def list_lifters(db: AsyncSession = Depends(get_db)):
#       ...
#
# Prednosti DI-ja:
#   - Endpoint ne zna kako se kreira DB sesija
#   - U testovima možemo podmetnuti mock sesiju
#   - Resursi se automatski zatvaraju nakon requesta
#
# Za sada prazan — popunjavamo u sljedećim predavanjima.
# =============================================================
from typing import AsyncGenerator

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.core.errors import AppError
from app.core.jwt import decode_token
from app.models.user import User
from app.repositories import user_repo

# HTTPBearer automatski čita "Authorization: Bearer <token>" header.
# auto_error=False: ne baca 403, mi sami bacamo 401.
_bearer_scheme = HTTPBearer(auto_error=False)



async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency koja daje DB sesiju za svaki request.

    Tijek:
      1. Kreira novu async sesiju
      2. yield → endpoint je koristi (SELECT, INSERT, …)
      3. Ako nema iznimke → commit (spremanje promjena)
      4. Ako je iznimka → rollback (poništavanje)
      5. finally → sesija se zatvara (vraća konekciju u pool)

    Zašto session-per-request?
      - Svaki request ima izoliranu transakciju
      - Nema "curenja" stanja između dva paralelna requesta
      - Automatski cleanup — nema zaboravljenih otvorenih konekcija
    """

    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Dependency koja izvlači i validira korisnika iz JWT tokena.

    Tijek:
      1. HTTPBearer čita Authorization: Bearer <token> header
      2. Dekodira token i provjerava potpis i expiry
      3. Provjerava je li type == "access" (ne refresh!)
      4. Dohvaća korisnika iz baze i provjerava is_active

    Korištenje u routeru:
      @router.get("/clubs")
      async def list_clubs(user: User = Depends(get_current_user)):
          ...
    """
    if credentials is None:
        raise AppError("invalid_credentials", "Token nije poslan.", 401)

    try:
        payload = decode_token(credentials.credentials)
    except JWTError:
        raise AppError("token_expired", "Token je istekao ili nije valjan.", 401)

    # Sprječava korištenje refresh tokena kao access tokena
    if payload.get("type") != "access":
        raise AppError("invalid_credentials", "Token nije access tipa.", 401)

    user = await user_repo.get_by_id(db, int(payload["sub"]))
    if not user or not user.is_active:
        raise AppError("invalid_credentials", "Korisnik ne postoji ili je deaktiviran.", 401)  # noqa: E501

    return user
def require_role(*allowed_roles: str):
    """
    Factory dependency: propušta samo korisnike s navedenom rolom.

    Korištenje:
      @router.post("/clubs")
      async def create_club(admin: User = Depends(require_role("admin"))):
          ...

      @router.get("/clubs")
      async def list_clubs(user: User = Depends(require_role("admin", "member"))):
          ...

    Ako korisnik nema odgovarajuću rolu → 403 Forbidden.
    401 = nisi prijavljen (tko si ti?)
    403 = prijavljen si, ali nemaš pravo (što smiješ?)
    """

    def checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise AppError("forbidden", "Nemate dozvolu za ovu akciju.", 403)
        return current_user

    return checker
