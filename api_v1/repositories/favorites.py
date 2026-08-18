from fastapi import HTTPException
from sqlalchemy import select, delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from core.models import Product, favorites_table


async def get_favorites(user_id: int, session: AsyncSession):
    stmt = (
        select(Product.id)
        .join(favorites_table, favorites_table.c.product_id == Product.id)
        .where(favorites_table.c.user_id == user_id)
    )
    favorites = await session.execute(stmt)
    return favorites.scalars().all()


async def add_favorite(user_id: int, product_id: int, session: AsyncSession):
    stmt = favorites_table.insert().values(user_id=user_id, product_id=product_id)
    try:
        await session.execute(stmt)
    except IntegrityError:
        raise HTTPException(400, "Bad request")
    await session.commit()
    return "success"


async def delete_favorite(user_id: int, product_id: int, session: AsyncSession):
    stmt = delete(favorites_table).where(
        favorites_table.c.user_id == user_id, favorites_table.c.product_id == product_id
    )
    result = await session.execute(stmt)
    if result.rowcount == 0:
        await session.rollback()
        raise HTTPException(status_code=404, detail="Favorite not found")
    await session.commit()
    return None
