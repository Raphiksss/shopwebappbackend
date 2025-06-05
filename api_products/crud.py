import base64
from typing import Optional
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.datastructures import UploadFile
from unicodedata import category
from api_products.schemas import ProductCreate, ProductRead, ProductUpdatePartial
from core.models import Product


async def create_product_crud(session: AsyncSession, product_in: ProductCreate, file: UploadFile,) -> Product:
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Пустой файл")
    product = Product(
            title = product_in.title,
            description = product_in.description,
            price = product_in.price,
            category = product_in.category,
            data = content,
            mimetype = file.content_type,

    )
    session.add(product)
    await session.commit()
    await session.refresh(product)
    return product


async def get_products_crud(session:AsyncSession):
    stmt = select(Product).order_by(Product.id)
    result = await session.execute(stmt)
    products = result.scalars().all()
    output = []
    for prod in products:
        b64 = base64.b64encode(prod.data).decode("ascii")
        output.append(
            ProductRead(
                id=prod.id,
                title=prod.title,
                description=prod.description,
                price=prod.price,
                image_b64=f"data:{prod.mimetype};base64,{b64}"
            )
        )
    return output

async def update_title(session: AsyncSession, product: Product, new_title: str ):
    product.title = new_title
    await session.commit()
    await session.refresh(product)
    return product


async def update_description(session: AsyncSession, product: Product, new_description :  str):
    product.description = new_description
    await session.commit()
    await session.refresh(product)
    return product


