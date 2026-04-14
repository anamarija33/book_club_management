# =============================================================
# membership_service.py — Poslovna logika za prijave u klub
# =============================================================
# Workflow:
#   1. Member šalje zahtjev → status: pending
#   2. Admin odobrava ili odbija → approved / rejected
#   3. Member može odustati (delete) dok je pending
#
# Poslovna pravila:
#   - Dupla prijava istog usera u isti klub → 409
#   - Klub pun (max_members dostignut) → 409
#   - Prijava nakon registration_deadline → 400
#   - Member smije vidjeti/brisati samo svoje prijave
#   - Admin smije sve
# =============================================================

from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.models.membership import Membership
from app.models.user import User
from app.repositories import club_repo, membership_repo


async def _get_club_or_404(db, club_id):
    from app.repositories import club_repo
    club = await club_repo.get_by_id(db, club_id)
    if not club:
        raise AppError("not_found", "Klub nije pronađen.", 404)
    return club


async def _get_membership_or_404(db, membership_id):
    m = await membership_repo.get_by_id(db, membership_id)
    if not m:
        raise AppError("not_found", "Prijava nije pronađena.", 404)
    return m


async def list_memberships(
    db: AsyncSession, club_id: int, current_user: User
) -> list[Membership]:
    """
    Admin vidi sve prijave za klub.
    Member vidi samo svoje prijave.
    """
    await _get_club_or_404(db, club_id)

    if current_user.role == "admin":
        return await membership_repo.get_by_club(db, club_id)

    # Member vidi samo svoju prijavu za taj klub
    existing = await membership_repo.get_existing(db, current_user.id, club_id)
    return [existing] if existing else []


async def create_membership(
    db: AsyncSession, club_id: int, current_user: User
) -> Membership:
    """
    Member se prijavljuje u klub.
    Provjere:
      - Rok za prijavu nije prošao
      - Korisnik već nije prijavljen
      - Klub nije pun
    """
    club = await _get_club_or_404(db, club_id)

    # Provjera roka
    now = datetime.now(timezone.utc)
    deadline = club.registration_deadline
    if deadline.tzinfo is None:
        deadline = deadline.replace(tzinfo=timezone.utc)
    if now > deadline:
        raise AppError(
            "deadline_passed",
            "Rok za prijavu u klub je istekao.",
            400,
        )

    # Dupla prijava
    existing = await membership_repo.get_existing(db, current_user.id, club_id)
    if existing:
        raise AppError(
            "already_member",
            "Već ste prijavljeni u ovaj klub.",
            409,
        )

    # Provjera kapaciteta
    approved_count = await membership_repo.count_approved(db, club_id)
    if approved_count >= club.max_members:
        raise AppError(
            "club_full",
            "Klub je popunjen — nema slobodnih mjesta.",
            409,
        )

    membership = Membership(user_id=current_user.id, club_id=club_id)
    return await membership_repo.create(db, membership)


async def update_membership_status(
    db: AsyncSession,
    club_id: int,
    membership_id: int,
    new_status: str,
    current_user: User,
) -> Membership:
    """
    Admin odobrava ili odbija prijavu.
    Provjera: ako odobravamo, klub ne smije biti pun.
    """
    await _get_club_or_404(db, club_id)
    membership = await _get_membership_or_404(db, membership_id)

    if membership.club_id != club_id:
        raise AppError("not_found", "Prijava nije pronađena.", 404)

    if new_status == "approved":
        club = await club_repo.get_by_id(db, club_id)
        approved_count = await membership_repo.count_approved(db, club_id)
        if approved_count >= club.max_members:
            raise AppError(
                "club_full",
                "Ne može se odobriti — klub je popunjen.",
                409,
            )

    membership.status = new_status
    await db.flush()
    return membership


async def delete_membership(
    db: AsyncSession,
    club_id: int,
    membership_id: int,
    current_user: User,
) -> None:
    """
    Member odustaje od prijave (samo svoje, samo pending).
    Admin može obrisati bilo koju prijavu.
    """
    await _get_club_or_404(db, club_id)
    membership = await _get_membership_or_404(db, membership_id)

    if membership.club_id != club_id:
        raise AppError("not_found", "Prijava nije pronađena.", 404)

    if current_user.role == "member":
        if membership.user_id != current_user.id:
            raise AppError("forbidden", "Ne možete obrisati tuđu prijavu.", 403)
        if membership.status != "pending":
            raise AppError(
                "invalid_status",
                "Možete povući samo prijave sa statusom pending.",
                400,
            )

    await db.delete(membership)
    await db.flush()
