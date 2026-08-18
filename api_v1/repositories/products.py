from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from core.models import Product
from ..schemas.products import ProductUpdate


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


async def delete_product(session: AsyncSession, product: Product | None) -> None:
    result = await session.delete(product)
    await session.commit()
    return result


async def partial_update_product(
    session: AsyncSession, product: Product, new_product: ProductUpdate
):
    print(new_product.model_dump())
    for name, value in new_product.model_dump(
        exclude_unset=True, exclude_none=True
    ).items():
        setattr(product, name, value)
    await session.commit()
    await session.refresh(product)
    return product
