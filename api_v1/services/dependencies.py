from typing import Optional, Type
from core.db_helper import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from core.models import Product
from ..schemas.products import ProductCreate
from fastapi import Form, UploadFile, File, HTTPException, Depends, status


def text_data(
    title: str =Form(..., description = "Название товара"),
    description: str = Form(..., description= "Описание товара") ,
    price: int = Form(..., description="Цена товара"),
    rating: float = Form(..., description="Рейтинг товара"),
    category: str | None = Form(..., description="Категория для товара"),
    product_type: str = Form("instantly", description="Тип товара")

) ->"ProductCreate":
    return ProductCreate(title = title, description = description, price = price,  rating = rating, category = category, product_type = product_type)

def upload_foto(
    img: UploadFile = File(..., description="Изображение"),
    ) -> UploadFile:
    allowed = {"image/png", "image/jpeg", "image/webp"}
    if img.content_type not in allowed:
        raise HTTPException(415, "Некоректный формат файла")
    return img


async def get_product_dp(product_id: int, session: AsyncSession = Depends(get_session)) -> Type[Product] | None:
    product = await session.get(Product, product_id)
    if not product:
        raise HTTPException(404, detail="Товар не найден")
    return product



