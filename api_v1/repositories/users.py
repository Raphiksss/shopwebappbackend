from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from core.models import User


async def create_user(user: User, session: AsyncSession) -> User:
    session.add(user)
    await session.commit()
    return user

async def get_user(tg_id: int, session: AsyncSession) -> User:
    stmt = select(User).where(User.tg_id == tg_id)
    res = await session.execute(stmt)
    return res.scalars().one_or_none()

async def get_users(session: AsyncSession):
    stmt = select(User).order_by(User.id)
    users = await session.execute(stmt)
    return users.scalars().all()

async def add_balance(tg_id: int, amount: int, session: AsyncSession):
    user = await get_user(tg_id, session)
    user.balance += amount
    await session.commit()
    return user
