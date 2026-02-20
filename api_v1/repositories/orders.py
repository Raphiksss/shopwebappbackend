from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import joinedload, selectinload
from ..schemas.orders import PartialOrderUpdate
from core.models import Order,OrdersItem


async def create_order(order: Order, session: AsyncSession) -> Order:
    session.add(order)
    await session.commit()
    await session.refresh(order)
    return order

async def get_orders(session: AsyncSession,filter:str|None,page:int|None,limit:int|None) -> List[Order]:
    stmt = select(Order).options(
        selectinload(Order.items)
            .selectinload(OrdersItem.product_rel),
        selectinload(Order.user_rel)).order_by(Order.id)

    if filter:
        stmt = stmt.filter(Order.status == filter)
    if page and limit:
        stmt = stmt.offset((page - 1) * limit).limit(limit)

    res = await session.execute(stmt)

    orders = res.scalars().all()
    return list(orders)

async def partial_order_update(order:Order,new_order:PartialOrderUpdate,session:AsyncSession):
    for name,value in new_order.model_dump(exclude_none=True,exclude_unset=True).items():
        setattr(order,name,value)
    await session.commit()
    await session.refresh(order)
    return order