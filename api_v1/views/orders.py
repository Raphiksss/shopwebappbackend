import asyncio
from typing import Optional

from fastapi import APIRouter, Depends
from starlette import status
from ..schemas.general import ErrorResponse

from core.db_helper import get_session
from ..schemas.orders import CreateOrder,PartialOrderUpdate,ReadOrders
from sqlalchemy.ext.asyncio import AsyncSession
from ..services import orders,auth

router = APIRouter(tags = ["Orders"])


@router.post("/", summary = "Create Order", status_code = status.HTTP_201_CREATED)
async def create_order(tg_id: int, session: AsyncSession = Depends(get_session)):
    res = await orders.create_order(tg_id, session)
    return res

@router.get("/", summary="Get Orders",status_code=status.HTTP_200_OK,response_model=list[ReadOrders],responses={401: {"model":ErrorResponse,"description":"Не авторизован"}})
async def get_orders(status:Optional[str] = None,session: AsyncSession = Depends(get_session),_=Depends(auth.check_if_auth)):
    return await orders.get_orders(status, session)


@router.patch("/{order_id}/",summary="Order Partial Update",status_code=status.HTTP_200_OK,responses={
    401: {"model":ErrorResponse,"description":"Не авторизован"},
    404: {"model":ErrorResponse,"description": "Заказ не найден"}
})
async def update_order_partial(order_id:int,new_order:PartialOrderUpdate,session:AsyncSession = Depends(get_session), _=Depends(auth.check_if_auth)):
    return await orders.product_partial_update(order_id,new_order,session)
