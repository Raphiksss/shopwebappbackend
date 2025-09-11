from fastapi import APIRouter, Depends, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from core.db_helper import get_session
from ..schemas.products import ProductRead,ProductCreate
from ..schemas import general
from ..services.dependencies import text_data, upload_foto
from core import s3_client
from ..services import products_services
from fastapi import status


router = APIRouter(tags = ["Products"])


@router.post("/", response_model=ProductRead, summary = "Create a new product",status_code = status.HTTP_201_CREATED)
async def create_product(data:ProductCreate = Depends(text_data), img: UploadFile = Depends(upload_foto), session:AsyncSession = Depends(get_session)):
    image_url = await s3_client.upload_file(img)
    return await products_services.create_product(data, image_url, session)

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