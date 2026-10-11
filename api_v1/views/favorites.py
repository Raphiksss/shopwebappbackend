from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .dependencies import get_users_tg_id
from ..schemas.general import ErrorResponse
from core.db_helper import get_session
from ..services import favorites_services

router = APIRouter(tags=["Favorites"])


@router.get("/", summary="Get users favorites", status_code=status.HTTP_200_OK)
async def get_favorites(session: AsyncSession = Depends(get_session), tg_id: int = Depends(get_users_tg_id)):
    return await favorites_services.get_favorites(tg_id, session)


@router.post(
    "/",
    summary="Add Favorite",
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {
            "model": ErrorResponse,
            "description": "Отсутствие такого товара в бд или он уже имеется в избранном у этого пользователя",
        }
    },
)
async def add_favorite(
    product_id: int, session: AsyncSession = Depends(get_session), tg_id: int = Depends(get_users_tg_id)
):
    return await favorites_services.add_favorite(tg_id, product_id, session)


@router.delete(
    "/",
    summary="Delete favorite",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        404: {
            "model": ErrorResponse,
            "description": "Отсутствие такого товара у пользователя",
        }
    },
)
async def delete_favorite(
    product_id: int, session: AsyncSession = Depends(get_session), tg_id: int = Depends(get_users_tg_id)
):
    return await favorites_services.delete_favorite(tg_id, product_id, session)
