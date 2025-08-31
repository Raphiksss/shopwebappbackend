from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy import select,delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from api_users.crud import get_user
from .schemas import UserCreate
from core.db_helper import get_session
from core.models import Product, favorites_table, User

router = APIRouter(tags = ["Users"])

@router.get("/get_user/{tg_id}/", summary = "Получить пользователя по тг-айди")
async def get_user_by_tg_id(tg_id: int, session: AsyncSession = Depends(get_session) ):
    profile = await get_user(tg_id = tg_id, session=session)
    return profile

@router.post("/create_user/", summary = "Создать пользователя")
async def create_user(user: UserCreate, session:AsyncSession = Depends(get_session)):
    user = User(**user.model_dump())
    session.add(user)
    await session.commit()

@router.get("/users/{user_id}/favorites",response_model=list[int],summary="ID товаров, добавленных пользователем в избранное")
async def list_favorites(user_id: int, session: Session = Depends(get_session)):
    stmt = (
        select(Product.id)
        .join(favorites_table, favorites_table.c.product_id == Product.id)
        .where(favorites_table.c.user_id == user_id)
    )
    fv = await session.scalars(stmt)
    return fv

@router.post(
    "/users/{user_id}/favorites/{product_id}",
    status_code=status.HTTP_201_CREATED,
    summary="Добавить товар в избранное"
)
async def add_favorite(
    user_id: int,
    product_id: int,
    session: Session = Depends(get_session)
):
    await session.execute(
        favorites_table.insert().values(
            user_id=user_id,
            product_id=product_id
        ).prefix_with("OR IGNORE")
    )
    await session.commit()
    return {"detail": "Added to favorites"}


@router.delete(
    "/users/{user_id}/favorites/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Убрать товар из избранного"
)
async def remove_favorite(
    user_id: int,
    product_id: int,
    session: Session = Depends(get_session)
):
    result = session.execute(
        delete(favorites_table)
        .where(
            favorites_table.c.user_id    == user_id,
            favorites_table.c.product_id == product_id
        )
    )
    if not result:
        raise HTTPException(status_code=404, detail="Favorite not found")
    await session.commit()


