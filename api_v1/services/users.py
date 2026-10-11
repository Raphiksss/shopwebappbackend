from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ..repositories import users_repository
from ..repositories.users import User, UserBy
from ..schemas import users_schemas, messages
from core.rabbitmq import publish_stars_replenishment, publish_crypto_bot_replenishment


async def create_user(user: users_schemas.UserCreate, session: AsyncSession):
    user = User(**user.model_dump())
    try:
        res = await users_repository.create_user(user, session)
    except IntegrityError:
        raise HTTPException(status_code=409, detail="User already exists")
    return res


async def get_user(session: AsyncSession, by: UserBy, value: int|str) -> User:
    res = await users_repository.get_user(session, by, value)
    if not res:
        raise HTTPException(status_code=404, detail="User not found")
    return res


async def update_user_partial(
    user_id: int, new_user: users_schemas.UserPartialUpdate, session: AsyncSession
):
    user = await get_user(session, UserBy.ID, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    new_user = await users_repository.update_user_partial(new_user, user, session)
    await session.refresh(user)
    return user


async def replenishment_balance_stars(tg_id: int, amount: int):
    message = messages.ReplenismentMessage(tg_id=tg_id, amount=amount)
    await publish_stars_replenishment(message.model_dump())

    return "success"


async def replenishment_balance_crypto_bot(tg_id: int, amount: int):
    message = messages.ReplenismentMessage(tg_id=tg_id, amount=amount)
    await publish_crypto_bot_replenishment(message.model_dump())

    return "success"
