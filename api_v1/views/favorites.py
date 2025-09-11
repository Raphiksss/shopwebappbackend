from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from ..schemas.general import ErrorResponse
from core.db_helper import get_session
from ..repositories import favorites_repository

router = APIRouter(tags = ["Favorites"])

@router.get("/{user_id}/", summary = "Get users favorites", status_code = status.HTTP_200_OK)
async def get_favorites(user_id: int, session: AsyncSession = Depends(get_session)):
    return await favorites_repository.get_favorites(user_id, session)

@router.post('/{user_id}/', summary = "Add Favorite", status_code = status.HTTP_201_CREATED,
            responses={
                400:{"model": ErrorResponse, "description": "Отсутствие такого товара в бд или он уже имеется в избранном у этого пользователя"
                     }
 })
async def add_favorite(user_id: int, product_id: int, session: AsyncSession = Depends(get_session)):
    return await favorites_repository.add_favorite(user_id, product_id,  session)

@router.delete("/{user_id}/", summary = "Delete favorite", status_code = status.HTTP_204_NO_CONTENT,
               responses={
                   404:{"model": ErrorResponse, "description": "Отсутствие такого товара у пользователя" }
               })
async def delete_favorite(user_id: int, product_id: int, session: AsyncSession = Depends(get_session)):
    return await favorites_repository.delete_favorite(user_id, product_id, session)