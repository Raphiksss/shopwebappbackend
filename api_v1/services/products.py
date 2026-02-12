from pydantic import TypeAdapter
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from core.models import Product
from ..repositories import products as prod_repo
from ..schemas.products import ProductCreate, ProductRead,ProductUpdate,ProductUpdateStrings
from .dependencies import get_product_dp
from fastapi import HTTPException


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
    try:
        created = await prod_repo.create_product(session,new_product)
    except IntegrityError:
        raise HTTPException(status_code=404, detail="Referenced resource not found")

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

async def partial_update_product(product_id:int, new_products_data:ProductUpdateStrings,image_url:str|None,data_url:str|None, session:AsyncSession) -> ProductRead:
    product = await get_product_dp(product_id,session)
    update_data = new_products_data.model_dump(exclude_unset=True)
    if image_url is not None:
        update_data["image"] = image_url
    if data_url is not None:
        update_data["product_data"] = data_url
    updated_product = ProductUpdate(**update_data)
    product = await prod_repo.partial_update_product(session=session,product=product,new_product=updated_product)
    return ProductRead.model_validate(product)