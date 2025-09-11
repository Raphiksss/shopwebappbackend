from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from core.models import Product


async def create_product(session: AsyncSession, product: Product) -> Product:
    session.add(product)
    await session.commit()
    await session.refresh(product)
    return product

async def get_products(session: AsyncSession) -> list[Product]:
    stmt = select(Product).order_by(Product.id)
    products = await session.execute(stmt)
    result = products.scalars()
    return list(result)

async def delete_product(session: AsyncSession, product: Product| None) -> None:
    result = await session.delete(product)
    await session.commit()
    return result
