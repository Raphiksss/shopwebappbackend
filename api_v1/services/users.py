from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from core.models import User
from ..repositories import users_repository
from ..schemas import users_schemas

async def create_user(user: users_schemas.UserCreate, session: AsyncSession):
    user = User(**user.model_dump())
    try:
        res = await users_repository.create_user(user, session)
    except IntegrityError:
        raise HTTPException(status_code=409, detail="User already exists")
    return res

async def get_user(tg_id: int, session: AsyncSession):
    res = await users_repository.get_user(tg_id, session)
    if not res:
        raise HTTPException(status_code=404, detail='User not found')
    return res




