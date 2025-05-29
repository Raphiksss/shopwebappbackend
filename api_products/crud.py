from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.datastructures import UploadFile
from api_products.schemas import ProductCreate
from core.models import Product


async def create_product_crud(session: AsyncSession, product_in: ProductCreate, file: UploadFile,) -> Product:
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Пустой файл")
    product = Product(
            title = product_in.title,
            description = product_in.description,
            price = product_in.price,
            data = content,
            mimetype = file.content_type,
    )
    session.add(product)
    await session.commit()
    await session.refresh(product)
    return product




