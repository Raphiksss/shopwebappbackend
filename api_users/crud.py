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






