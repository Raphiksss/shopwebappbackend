from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from core.models import Category

async def create_category(category: Category, session: AsyncSession) -> Category:
    session.add(category)
    await session.commit()
    await session.refresh(category)
    return category

async def get_categories(session: AsyncSession) -> list[Category]:
    stmt = select(Category).order_by(Category.id)
    products = await session.execute(stmt)
    result = products.scalars().all()
    return result

async def delete_category(category_id:int, session: AsyncSession) -> None:
    stmt = delete(Category).where(Category.id == category_id)
    await session.execute(stmt)
    return None


