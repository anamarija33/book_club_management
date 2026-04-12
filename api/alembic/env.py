# =============================================================
# alembic/env.py — Okruženje za pokretanje migracija
# =============================================================
# Ova datoteka govori Alembicu KAKO se spojiti na bazu i
# ODAKLE čitati metadata (definicije tablica).
#
# Ključne prilagodbe u odnosu na default:
#   1. Koristimo ASYNC engine (asyncpg driver)
#   2. URL čitamo iz app.core.config.settings (ne iz alembic.ini)
#   3. target_metadata = Base.metadata (naši modeli)
#
# VAŽNO: import "from app.models import Base" MORA biti tu
# jer taj import pokreće registraciju svih modela u Base.metadata.
# Bez toga, autogenerate ne vidi nijednu tablicu!
# =============================================================

import asyncio
import sys
from logging.config import fileConfig
from pathlib import Path

# Dodajemo api/ direktorij na sys.path tako da Alembic može
# importirati "app" paket. Bez ovoga: ModuleNotFoundError.
# Path(__file__) → alembic/env.py → .parent.parent → api/
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine  # noqa: E402

from alembic import context  # noqa: E402
from app.core.config import settings  # noqa: E402
from app.models import Base  # noqa: E402, F401 — registrira sve modele

config = context.config

# Postavljamo URL programski (umjesto iz .ini datoteke).
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata koji Alembic koristi za autogenerate.
# Base.metadata sadrži definicije SVIH tablica (User, Club, Membership...).
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    connectable = create_async_engine(
        config.get_main_option("sqlalchemy.url"),
        pool_pre_ping=True,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
