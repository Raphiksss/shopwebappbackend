from typing import Optional
from core.db_helper import get_session
from sqlalchemy.ext.asyncio import AsyncSession
from core.models import Product
from .schemas import ProductCreate
from fastapi import Form, UploadFile, File, HTTPException, Depends


def text_data(
    title: str =Form(..., description = "Название товара"),
    description: str = Form(..., description= "Описание товара") ,
    price: int = Form(..., description="Цена товара"),
) ->"ProductCreate":
    return ProductCreate(title = title, description = description, price = price)

def upload_foto(
    file: UploadFile = File(..., description="Изображение"),
    ) -> UploadFile:
    allowed = {"image/png", "image/jpeg", "image/webp"}
    if file.content_type not in allowed:
        raise HTTPException(415, f"Недопустимый тип файла: {file.content_type}")
    return file
