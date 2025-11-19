from sqlalchemy.ext.asyncio.session import AsyncSession
from core.models import Order


async def create_order(order: Order, session: AsyncSession) -> Order:
    session.add(order)
    await session.commit()
    return order

