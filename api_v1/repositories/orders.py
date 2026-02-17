from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import joinedload

from core.models import Order


async def create_order(order: Order, session: AsyncSession) -> Order:
    session.add(order)
    await session.commit()
    await session.refresh(order)
    return order

async def get_orders(session: AsyncSession) -> List[Order]:
    stmt = select(Order).options(joinedload(Order.items)).order_by(Order.id)
    res = await session.execute(stmt)
    orders = res.scalars().unique()
    return list(orders)