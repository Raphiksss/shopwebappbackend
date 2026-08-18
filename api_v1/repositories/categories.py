from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession, session
from core.models import Category
from ..schemas.categories import CategoryPartialUpdate


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


async def get_category(category_id: int, session: AsyncSession) -> Category | None:
    return await session.get(Category, category_id)


async def category_partial_update(
    category: Category, new_category: CategoryPartialUpdate, session: AsyncSession
):
    for name, value in new_category.model_dump(
        exclude_unset=True, exclude_none=True
    ).items():
        setattr(category, name, value)
    await session.commit()
    await session.refresh(category)
    return category


async def delete_category(category_id: int, session: AsyncSession) -> None:
    stmt = delete(Category).where(Category.id == category_id)
    await session.execute(stmt)
    await session.commit()
    return None
