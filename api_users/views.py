from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api_users.crud import get_user
from core.db_helper import get_session

router = APIRouter(tags = ["Users"])

@router.get("/get_user/{tg_id}")
async def get_user_by_tg_id(session: AsyncSession = Depends(get_session), tg_id = int):
    profile = await get_user(tg_id = tg_id, session=session)
    return profile



