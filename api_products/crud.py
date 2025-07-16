import base64
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.datastructures import UploadFile
from api_products.schemas import ProductCreate, ProductRead
from core.models import Product
from core import s3_client

async def create_product_crud(session: AsyncSession, product_in: ProductCreate, file: UploadFile,) -> Product:
    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail = "Пустой файл")
    file.file.seek(0)
    object_name = await s3_client.upload_file(file)
    product = Product(
            title = product_in.title,
            subtitle = product_in.subtitle,
            description = product_in.description,
            price = product_in.price,
            category = product_in.category,
            rating = product_in.rating,
            image = f"http://localhost:9000/{s3_client.bucket_name}/{object_name}",


    )
    session.add(product)
    await session.commit()
    await session.refresh(product)
    return product


async def get_products_crud(session:AsyncSession):
    stmt = select(Product).order_by(Product.id)
    result = await session.execute(stmt)
    products = result.scalars().all()
    return products

async def update_title(session: AsyncSession, product: Product, new_title: str):
    product.title = new_title
    await session.commit()
    await session.refresh(product)
    return product


async def update_description(session: AsyncSession, product: Product, new_description :  str):
    product.description = new_description
    await session.commit()
    await session.refresh(product)
    return product

async def delete_product(session:AsyncSession, product: Product):
    await session.delete(product)
    await session.commit()
    return "success"

