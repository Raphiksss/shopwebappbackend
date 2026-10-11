from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ..repositories import favorites_repository as f_rp
from ..repositories import users_repository as u_rp
from ..repositories.users import UserBy


async def add_favorite(tg_id: int, product_id: int, session: AsyncSession):
    user = await u_rp.get_user(session, UserBy.TG_ID, tg_id)
    if not user:
        raise HTTPException(status_code=404, detail="Not Found")
    await f_rp.add_favorite(user.id, product_id, session)
    return "success"


async def get_favorites(tg_id: int, session: AsyncSession):
    user = await u_rp.get_user(session, UserBy.TG_ID, tg_id)
    if not user:
        raise HTTPException(status_code=404, detail="Not Found")
    res = await f_rp.get_favorites(user.id, session)
    return res


async def delete_favorite(tg_id: int, product_id: int, session: AsyncSession):
    user = await u_rp.get_user(session, UserBy.TG_ID, tg_id)
    if not user:
        raise HTTPException(status_code=404, detail="Not Found")
    await f_rp.delete_favorite(user.id, product_id, session)
    return "success"
