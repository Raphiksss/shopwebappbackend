from typing import Optional, Type
from core.db_helper import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from core.models import Product
from .schemas import ProductCreate
from fastapi import Form, UploadFile, File, HTTPException, Depends, status


def text_data(
    title: str =Form(..., description = "Название товара"),
    description: str = Form(..., description= "Описание товара") ,
    price: int = Form(..., description="Цена товара"),
    category: str | None = Form(..., description="Категория для товара"),
) ->"ProductCreate":
    return ProductCreate(title = title, description = description, price = price, category = category)

def upload_foto(
    file: UploadFile = File(..., description="Изображение"),
    ) -> UploadFile:
    allowed = {"image/png", "image/jpeg", "image/webp"}
    if file.content_type not in allowed:
        raise HTTPException(415, f"Недопустимый тип файла: {file.content_type}")
    return file


async def get_product_by_id_dp(product_id: int, session: AsyncSession = Depends(get_session)) -> Optional[Product]:
    product = await session.get(Product, product_id)
    return product



