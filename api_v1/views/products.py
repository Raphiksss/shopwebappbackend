import os
from typing import Optional

from fastapi import APIRouter, Depends, UploadFile, status, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from core.db_helper import get_session
from ..schemas.products import ProductRead,ProductCreate
from ..schemas import general
from ..services.dependencies import text_data, upload_foto
from core import s3_client
from ..services import products_services


router = APIRouter(tags = ["Products"])


@router.post("/", response_model=ProductRead, summary = "Create a new product",status_code = status.HTTP_201_CREATED)
async def create_product(text_data:ProductCreate = Depends(text_data), img: UploadFile = Depends(upload_foto), data: Optional[UploadFile] = None, session:AsyncSession = Depends(get_session)):
    image_url = await s3_client.upload_file(img)
    file_location = None
    if data:
        if data.size < (50 * 1024 * 1024):
            raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail = "Файл слишком большой")
        file_location = os.path.join("files",data.filename)
        with open(file_location, "wb") as f:
            content = await data.read()
            f.write(content)

    return await products_services.create_product(text_data, image_url, file_location, session)

@router.get("/", response_model = list[ProductRead], summary = "Get products", status_code = status.HTTP_200_OK)
async def get_products(session: AsyncSession = Depends(get_session)):
    return await products_services.get_products(session)

@router.get("/{product_id}/", response_model = ProductRead, summary = "Get product",
            status_code = status.HTTP_200_OK, responses = {
                404: {
                    "model": general.ErrorResponse,
                    "description": "Товар отсутвует"}})
async def get_product(product_id: int, session: AsyncSession = Depends(get_session)):
    return await products_services.get_product(product_id, session)

@router.delete("/{product_id}/", summary = "Delete product",status_code = status.HTTP_204_NO_CONTENT,
            responses={
            404: {
                "model": general.ErrorResponse,
                "description": "Товар отсутвует"}})
async def delete_products(product_id:int, session: AsyncSession = Depends(get_session)):
    return await products_services.delete_product(product_id, session)