from typing import List, TypedDict, Unpack
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from core.models import User
from ..schemas.users import UserPartialUpdate

from enum import StrEnum, auto


class UserBy(StrEnum):
    ID = auto()
    TG_ID = auto()
    USERNAME = auto()


async def create_user(user: User, session: AsyncSession) -> User:
    session.add(user)
    await session.commit()
    return user


async def get_user(session: AsyncSession, by: UserBy, value: int|str) -> User | None:
    stmt = select(User).where(getattr(User, by) == value)
    res = await session.execute(stmt)
    return res.scalars().one_or_none()


async def update_user_partial(
    new_user: UserPartialUpdate, user: User, session: AsyncSession
):
    for name, value in new_user.model_dump(
        exclude_none=True, exclude_unset=True
    ).items():
        setattr(user, name, value)
    await session.commit()
    await session.refresh(user)
    return user


async def get_users(session: AsyncSession):
    stmt = select(User).order_by(User.id)
    users = await session.execute(stmt)
    return users.scalars().all()


async def add_balance(tg_id: int, amount: int, session: AsyncSession):
    user = await get_user(session, UserBy.TG_ID, tg_id)
    user.balance += amount
    await session.commit()
    return user
