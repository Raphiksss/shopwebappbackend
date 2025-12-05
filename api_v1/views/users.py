from sqlalchemy.ext.asyncio import AsyncSession
from core.db_helper import get_session
from ..schemas.users import UserRead, UserCreate
from ..services import users_services
from fastapi import APIRouter, status, Depends
from ..repositories import users_repository
from ..schemas.general import ErrorResponse


router = APIRouter(tags = ["Users"])

@router.get("/", summary = "Get Users", status_code = status.HTTP_200_OK, response_model=list[UserRead])
async def get_users(session: AsyncSession = Depends(get_session)):
    return await users_repository.get_users(session)

@router.post("/", summary = "Create User", status_code = status.HTTP_201_CREATED, response_model=UserRead,
             responses = {
                 409:{"model":ErrorResponse, "description": "Пользователь с таким tg_id уже существует"}
             })
async def create_user(user:UserCreate, session: AsyncSession = Depends(get_session)):
    return await users_services.create_user(user, session)

@router.get("/{tg_id}/", summary = "Get User by tg_id", status_code = status.HTTP_200_OK, response_model = UserRead,
            responses = {
                404: {"model": ErrorResponse, "description": "Пользователя не существует"}
            })
async def get_user(tg_id: int, session: AsyncSession = Depends(get_session)):
    return await users_services.get_user(tg_id, session)

@router.post("/replenisment/stars/", summary = "Пополнение баланса пользователем", status_code = status.HTTP_200_OK)
async def replenishment_balance(tg_id: int, amount: int):
    return await users_services.replenishment_balance_stars(tg_id, amount)

@router.post("/replenisment/crypto/", summary = "Пополнение баланса пользователем", status_code = status.HTTP_200_OK)
async def replenishment_balance_cr(tg_id: int, amount: int):
    return await users_services.replenishment_balance_crypto_bot(tg_id, amount)