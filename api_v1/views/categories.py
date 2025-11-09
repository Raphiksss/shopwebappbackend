from fastapi import APIRouter, Depends, UploadFile, Form
from starlette import status
from ..schemas.categories import CategoryRead
from ..services.dependencies import upload_foto
from ..services import categories as categories_services
from sqlalchemy.ext.asyncio import AsyncSession
from core.db_helper import get_session
from core import s3_client

router = APIRouter(tags = ["Categories"])

@router.post("/", summary = "Create a new category", status_code = status.HTTP_201_CREATED, response_model = CategoryRead)
async def create_category(category_title:str = Form(...,description= "Название категории"), img:UploadFile = Depends(upload_foto), session: AsyncSession = Depends(get_session)):
    image_url = await s3_client.upload_file(img)
    return await categories_services.create_category(category_title, image_url, session)

@router.get("/", summary = "Get categories", status_code = status.HTTP_200_OK, response_model = list[CategoryRead])
async def get_categories(session: AsyncSession = Depends(get_session)):
    return await categories_services.get_categories(session)
