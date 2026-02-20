from typing import Optional

from fastapi import HTTPException
from sqlalchemy.ext.asyncio.session import AsyncSession
from ..repositories import categories
from core.models import Category
from ..schemas.categories import CategoryPartialUpdate


async def create_category(category_title: str, img_url: str, session: AsyncSession):
    nw_categories = Category(
        title = category_title,
        img = img_url)
    res = await categories.create_category(nw_categories, session)
    return res

async def get_categories(session: AsyncSession):
    res = await categories.get_categories(session)
    return list(res)

async def partial_category_update(category_id:int,new_title:Optional[str],image_url:Optional[str],session:AsyncSession):
    category = await categories.get_category(category_id,session)
    if not category:
        raise HTTPException(status_code=404,detail="Category not found")
    new_category = CategoryPartialUpdate(title=new_title,img=image_url)
    res = await categories.category_partial_update(category,new_category,session)
    return res