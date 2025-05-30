from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.datastructures import UploadFile
from .crud import create_product_crud, get_products_crud
from .schemas import ProductRead, ProductCreate
from core.db_helper import get_session
from .dependensiec import text_data,upload_foto


router = APIRouter(tags = ["Products"])

@router.post('/create_product', summary = "Создать товар с изображением")
async def create_product(session: AsyncSession = Depends(get_session),
                         product_in:ProductCreate = Depends(text_data),
                         file: UploadFile = Depends(upload_foto)
):
                        await create_product_crud(session, product_in, file)
                        return "succes"

@router.get('/get_products', summary = "Получение всех товаров", response_model = list[ProductRead])
async def get_products(session: AsyncSession = Depends(get_session)):
    products = await get_products_crud(session)
    return products




