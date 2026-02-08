#!/usr/bin/env python
import asyncio
import subprocess
import sys



sys.path.insert(0, '/backend')

from core.common import logger
from sqlalchemy import text
from core.db_helper import engine, AsyncSessionLocal
from core.models.Base import Base
from core.models.Admin import Admin
from core.config import settings
from api_v1.services import auth

async def check_db_empty():
    """Check if database has no tables."""
    print(f"DB URL: {settings.DB.db_url}")
    async with engine.connect() as conn:
        db = await conn.execute(text("SELECT current_database()"))
        print(f"Connected to database: {db.scalar()}")
        tables = await conn.execute(text(
            "SELECT tablename FROM pg_tables WHERE schemaname = 'public'"
        ))
        table_list = [row[0] for row in tables]
        print(f"Tables found: {table_list}")
        return len(table_list) == 0


async def create_tables():
    """Create all tables from models."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Tables created successfully")


async def create_initial_admin():
    """Create initial admin if not exists."""
    from sqlalchemy import select
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Admin).limit(1))
        admin = result.scalar_one_or_none()

        if admin is None:
            username = str(settings.ADMIN_USERNAME)
            password = str(settings.ADMIN_PASSWORD)
            logger.debug(f"username:{username}, password:{password}")
            await auth.create_admin(username,password,session)
            print(f"Created initial admin: {username}")
        else:
            print("Admin already exists, skipping creation")


def stamp_head():
    """Mark all migrations as applied without running them."""
    print("Stamping database with current head...")
    result = subprocess.run(
        ['alembic', 'stamp', 'head'],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        print(f"Stamp error: {result.stderr}")
    else:
        print("Database stamped successfully")


async def main():
    print("=== Database Initialization ===")

    is_empty = await check_db_empty()

    if is_empty:
        print("Database is empty, creating tables from models...")
        await create_tables()
        stamp_head()
    else:
        print("Database already has tables, skipping creation")

    await create_initial_admin()
    print("=== Initialization Complete ===")


if __name__ == '__main__':
    asyncio.run(main())
