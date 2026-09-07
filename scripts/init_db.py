#!/usr/bin/env python
import asyncio
import subprocess
import sys

sys.path.insert(0, "/backend")

from sqlalchemy import select

from core.db_helper import AsyncSessionLocal
from core.models.Admin import Admin
from core.config import settings
from api_v1.services import auth


def run_migrations():
    """Bring the schema to head, creating it from scratch on an empty database."""
    print("Running alembic upgrade head...")
    result = subprocess.run(
        ["alembic", "upgrade", "head"], capture_output=True, text=True
    )
    print(result.stdout)
    if result.returncode != 0:
        # serving traffic on a half-migrated schema corrupts data silently
        print(result.stderr, file=sys.stderr)
        sys.exit(1)
    print("Migrations applied successfully")


async def create_initial_admin():
    """Create initial admin if not exists."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Admin).limit(1))
        admin = result.scalar_one_or_none()

        if admin is None:
            username = str(settings.ADMIN_USERNAME)
            password = str(settings.ADMIN_PASSWORD)
            await auth.create_admin(username, password, session)
            print(f"Created initial admin: {username}")
        else:
            print("Admin already exists, skipping creation")


async def main():
    print("=== Database Initialization ===")
    print(f"DB NAME: {settings.DB.DB_NAME}")

    run_migrations()
    await create_initial_admin()

    print("=== Initialization Complete ===")


if __name__ == "__main__":
    asyncio.run(main())
