from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from api_users.schemas import UserCreate
from core.models import User


async def create_user(session: AsyncSession, user_in: UserCreate):
    user = User(**user_in.model_dump())
    try:
        session.add(user)
        await session.commit()
    finally:
        return "succes"


async def get_user(tg_id: int, session: AsyncSession):
    result = await session.execute(
        select(User).where(User.tg_id == tg_id)
    )
    return result.scalars().first()




