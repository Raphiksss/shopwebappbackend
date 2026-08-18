from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, Form, HTTPException
from starlette import status
from ..schemas.categories import CategoryRead
from ..services.dependencies import upload_foto
from ..services import categories as categories_services, auth
from sqlalchemy.ext.asyncio import AsyncSession
from core.db_helper import get_session
from core import s3_client
from ..repositories import categories as categories_repositories
from ..schemas.general import ErrorResponse
from ..services.images import upload_image

router = APIRouter(tags=["Categories"])


@router.post(
    "/",
    summary="Create a new category",
    status_code=status.HTTP_201_CREATED,
    response_model=CategoryRead,
)
async def create_category(
    category_title: str = Form(..., description="Название категории"),
    img: UploadFile = Depends(upload_foto),
    session: AsyncSession = Depends(get_session),
    _=Depends(auth.check_if_auth),
):
    image_url = await upload_image(img)
    return await categories_services.create_category(category_title, image_url, session)


@router.get(
    "/",
    summary="Get categories",
    status_code=status.HTTP_200_OK,
    response_model=list[CategoryRead],
)
async def get_categories(session: AsyncSession = Depends(get_session)):
    return await categories_services.get_categories(session)


@router.patch(
    "/{category_id}/",
    summary="Partial category update",
    status_code=status.HTTP_200_OK,
    responses={
        401: {"description": "Не авторизован"},
        403: {"description": "Категория не найдена"},
        415: {"description": "Некорректный формат файла"},
    },
)
async def partial_category_update(
    category_id: int,
    title: Optional[str] = Form(None),
    img: Optional[UploadFile] = None,
    session: AsyncSession = Depends(get_session),
    _=Depends(auth.check_if_auth),
):
    allowed = {"image/png", "image/jpeg", "image/webp"}
    image_url = None
    if img:
        if img.content_type not in allowed:
            raise HTTPException(415, "Некоректный формат файла")
        image_url = await upload_image(img)
    return await categories_services.partial_category_update(
        category_id, title, image_url, session
    )


@router.delete(
    "/{category_id}/", summary="Delete category", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_category(
    category_id: int,
    session: AsyncSession = Depends(get_session),
    _=Depends(auth.check_if_auth),
):
    await categories_repositories.delete_category(category_id, session)
    return None
