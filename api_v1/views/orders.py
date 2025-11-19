import asyncio

from fastapi import APIRouter, Depends
from starlette import status


from core.db_helper import get_session
from ..schemas.orders import CreateOrder
from sqlalchemy.ext.asyncio import AsyncSession
from ..services import orders

router = APIRouter(tags = ["Orders"])


@router.post("/", summary = "Create Order", status_code = status.HTTP_201_CREATED)
async def create_order(tg_id: int, session: AsyncSession = Depends(get_session)):
    res = await orders.create_order(tg_id, session)
    return res