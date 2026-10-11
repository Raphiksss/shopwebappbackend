from fastapi import APIRouter, status, Depends

from .dependencies import get_users_tg_id
from ..services import cart_services
from ..schemas.general import ErrorResponse

router = APIRouter(tags=["Cart"])


@router.post(
    "/", summary="Добавить в коризну", status_code=status.HTTP_201_CREATED
)
async def add_to_cart(prod_id: int, tg_id: int = Depends(get_users_tg_id)):
    return cart_services.add_product(tg_id=tg_id, prod_id=prod_id)


@router.get(
    "/", summary="Получить корзину пользователя", status_code=status.HTTP_200_OK
)
async def get_cart(tg_id: int = Depends(get_users_tg_id)):
    return cart_services.get_card(tg_id)


@router.delete(
    "/",
    summary="Удалить товар с корзины",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        404: {"model": ErrorResponse, "description": "Нету такого товара в корзине"}
    },
)
async def delete_product_from_cart(prod_id: int, tg_id: int = Depends(get_users_tg_id)):
    return cart_services.del_product(tg_id=tg_id, prod_id=prod_id)


@router.delete(
    "/all_cart/",
    summary="Удалить все с корзины",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_cart(tg_id: int = Depends(get_users_tg_id)):
    return cart_services.del_all_card(tg_id)


@router.delete(
    "/full_product/",
    summary="Удалить полностью один товар с корзины",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_full_one_product(prod_id: int, tg_id: int = Depends(get_users_tg_id)):
    return cart_services.del_all_one_product(tg_id, prod_id)
