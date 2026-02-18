from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import joinedload
from ..schemas.orders import PartialOrderUpdate
from core.models import Order


async def create_order(order: Order, session: AsyncSession) -> Order:
    session.add(order)
    await session.commit()
    await session.refresh(order)
    return order

async def get_orders(session: AsyncSession,filter:str|None) -> List[Order]:
    if filter:
        stmt = select(Order).options(joinedload(Order.items)).order_by(Order.id).filter(Order.status == filter)
    else:
        stmt = select(Order).options(joinedload(Order.items)).order_by(Order.id)
    res = await session.execute(stmt)
    orders = res.scalars().unique()
    return list(orders)

async def partial_order_update(order:Order,new_order:PartialOrderUpdate,session:AsyncSession):
    for name,value in new_order.model_dump(exclude_none=True,exclude_unset=True).items():
        setattr(order,name,value)
    await session.commit()
    await session.refresh(order)
    return order