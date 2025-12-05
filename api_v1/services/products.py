
from pydantic import TypeAdapter
from sqlalchemy.ext.asyncio import AsyncSession
from core.models import Product
from ..repositories import products as prod_repo
from ..schemas.products import ProductCreate, ProductRead
from .dependencies import get_product_dp

async def create_product(data:ProductCreate,image_url:str, data_url:str, session:AsyncSession) -> ProductRead:
    new_product = Product(
        title = data.title,
        description = data.description,
        price = data.price,
        rating = data.rating,
        category_title = data.category,
        image = image_url,
        product_type = data.product_type,
        product_data = data_url
    )
    created = await prod_repo.create_product(session,new_product)
    return ProductRead.model_validate(created)

async def get_products(session:AsyncSession) -> list[ProductRead]:
    res = await prod_repo.get_products(session)
    return TypeAdapter(list[ProductRead]).validate_python(res)

async def get_product(product_id:int, session:AsyncSession) -> ProductRead:
    res = await get_product_dp(product_id,session)
    return ProductRead.model_validate(res)

async def delete_product(product_id:int ,session: AsyncSession) -> None:
    product = await get_product_dp(product_id, session)
    return await prod_repo.delete_product(session, product)