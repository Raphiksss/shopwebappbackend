
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.datastructures import UploadFile
from core.models import Product
from .crud import create_product_crud, get_products_crud, update_title, get_product
from .schemas import ProductRead, ProductCreate, ProductReturn
from core.db_helper import get_session
from .dependensiec import text_data,upload_foto, get_product_by_id


router = APIRouter(tags = ["Products"])

@router.post('/create_product/', summary = "Создать товар с изображением")
async def create_product(session: AsyncSession = Depends(get_session),
                         product_in:ProductCreate = Depends(text_data),
                         file: UploadFile = Depends(upload_foto)
):
                        await create_product_crud(session, product_in, file)
                        return "succes"

@router.get('/get_products/', summary = "Получение всех товаров", response_model = list[ProductRead])
async def get_products(session: AsyncSession = Depends(get_session)):
    products = await get_products_crud(session)
    return products

@router.get('/get_product/{product_id}/', summary = "Получить продукт по ID ", response_model = ProductRead )
async def get_product_by_id(product_id: int,session: AsyncSession = Depends(get_session)):
    product = await get_product(session, product_id)
    return product

@router.patch('/{product_id}/update_title/', summary = "Обновить название",)
async def path_title(new_title : str, product_id: int, product: Product = Depends(get_product_by_id), session: AsyncSession = Depends(get_session)):
    new_product = await update_title(session,product, new_title)
    return "succes"
#
# @router.patch('/{product_id}/update_description/', summary = "Обновить описание")
# async def path_description(new_title)


