import os
from typing import Optional

from fastapi import APIRouter, Depends, UploadFile, status, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from core.db_helper import get_session
from ..schemas.products import ProductRead, ProductCreate, ProductUpdate, ProductUpdateStrings
from ..schemas import general
from ..services.dependencies import text_data, upload_foto,text_data_partial
from core import s3_client
from ..services import products_services, auth

router = APIRouter(tags = ["Products"])


@router.post("/", response_model=ProductRead, summary = "Create a new product",status_code = status.HTTP_201_CREATED,responses = {
                401:{
                    "model": general.ErrorResponse,
                    "description": "Не авторизован"}
                ,
                404: {
                    "model": general.ErrorResponse,
                    "description": "Нарушен FK(Такой категории не существует)"},
                413: {
                    "model": general.ErrorResponse,
                    "description": "Файл слишком большой"
                },
                415: {
                    "model": general.ErrorResponse,
                    "description": "Некоректный формат файла"
                }
})
async def create_product(text_data:ProductCreate = Depends(text_data), img: UploadFile = Depends(upload_foto), data: Optional[UploadFile] = None, session:AsyncSession = Depends(get_session),_=Depends(auth.check_if_auth)):
    image_url = await s3_client.upload_file(img)
    file_location = None
    if data:
        if data.size > (50 * 1024 * 1024):
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

@router.patch("/{product_id}/",summary = "Partial product update",response_model=ProductRead, status_code = status.HTTP_200_OK,responses={
            404: {
                "model": general.ErrorResponse,
                "description": "Товар отсутвует"},
            401:{
                "model": general.ErrorResponse,
                "description": "Не авторизован"
            },
            413: {
                "model": general.ErrorResponse,
                "description": "Файл слишком большой"
                }
} )
async def product_partial_update(product_id:int,text_data:ProductUpdateStrings = Depends(text_data_partial),img:Optional[UploadFile] = None,data:Optional[UploadFile] = None,session:AsyncSession = Depends(get_session), _=Depends(auth.check_if_auth)):
    image_url = None
    data_url = None
    if img:
        image_url = await s3_client.upload_file(img)
    if data:
        if data.size > (50 * 1024 * 1024):
            raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail = "Файл слишком большой")
        data_url = os.path.join("files",data.filename)
        with open(data_url, "wb") as f:
            content = await data.read()
            f.write(content)
    return await products_services.partial_update_product(product_id=product_id,new_products_data=text_data,image_url=image_url,data_url=data_url, session=session)

@router.delete("/{product_id}/", summary = "Delete product",status_code = status.HTTP_204_NO_CONTENT,
            responses={
            404: {
                "model": general.ErrorResponse,
                "description": "Товар отсутвует"}}, )
async def delete_products(product_id:int, session: AsyncSession = Depends(get_session), _=Depends(auth.check_if_auth)):
    return await products_services.delete_product(product_id, session)