from sqlalchemy.ext.asyncio.session import AsyncSession
from ..repositories import categories
from core.models import Category

async def create_category(category_title: str, img_url: str, session: AsyncSession):
    nw_categories = Category(
        title = category_title,
        img = img_url)
    res = await categories.create_category(nw_categories, session)
    return res

async def get_categories(session: AsyncSession):
    res = await categories.get_categories(session)
    return list(res)