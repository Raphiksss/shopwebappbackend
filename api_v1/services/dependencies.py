from typing import Optional, Type
from pydantic_core import ValidationError
from core.db_helper import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from core.models import Product, User
from ..schemas.products import ProductCreate, ProductUpdateStrings
from fastapi import Form, UploadFile, File, HTTPException, Depends, status


def text_data(
    title: str = Form(..., description="Название товара"),
    description: str = Form(..., description="Описание товара"),
    price: int = Form(..., description="Цена товара"),
    rating: float = Form(..., description="Рейтинг товара"),
    category: str | None = Form(..., description="Категория для товара"),
    product_type: str = Form("notinstantly", description="Тип товара"),
) -> "ProductCreate":
    return ProductCreate(
        title=title,
        description=description,
        price=price,
        rating=rating,
        category=category,
        product_type=product_type,
    )


def text_data_partial(
    title: str | None = Form(None, description="Название товара"),
    description: str | None = Form(None, description="Описание товара"),
    price: str | None = Form(None, description="Цена товара"),
    rating: str | None = Form(None, description="Рейтинг товара"),
    category: str | None = Form(None, description="Категория для товара"),
    product_type: str | None = Form(None, description="Тип товара"),
) -> "ProductUpdateStrings":
    try:
        return ProductUpdateStrings(
            title=title,
            description=description,
            price=price,
            rating=rating,
            category_title=category,
            product_type=product_type,
        )
    except ValidationError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Некорректные данные",
        )


def upload_foto(
    img: Optional[UploadFile] = File(..., description="Изображение"),
) -> UploadFile | None:
    if not img:
        return None
    allowed = {"image/png", "image/jpeg", "image/webp"}
    if img.content_type not in allowed:
        raise HTTPException(415, "Некоректный формат файла")
    return img


async def get_product_dp(
    product_id: int, session: AsyncSession = Depends(get_session)
) -> Type[Product] | None:
    product = await session.get(Product, product_id)
    if not product:
        raise HTTPException(404, detail="Товар не найден")
    return product


async def get_user_dp(user_id: int, session: AsyncSession) -> Type[User]:
    user = await session.get(User, user_id)
    print("d")
    if not user:
        raise HTTPException(404, detail="Пользователь не найден")
    return user
