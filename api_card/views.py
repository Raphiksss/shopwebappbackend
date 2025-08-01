from fastapi import APIRouter
from .crud import add_product, get_card, del_product, del_all_card

router = APIRouter(tags = ["Cart"])

@router.post("/add_to_cart/{tg_id}/", summary = "Добавить в коризну")
async def add_to_cart(tg_id: int, prod_id: int):
    add_product(tg_id = tg_id, prod_id = prod_id)
    return "succes"

@router.get("/get_cart/{tg_id}/", summary = "Получить корзину пользователя")
async def get_cart(tg_id:int):
    return get_card(tg_id)

@router.delete("/delete_from_cart/", summary = "Удалить товар из корзины")
async def delete_product_from_cart(tg_id:int, prod_id = int):
    del_product(tg_id = tg_id, prod_id = prod_id)
    return "succes"

@router.delete("/delete_cart/{tg_id}/", summary = "Удалить все с корзины")
async def delete_cart(tg_id:int):
    del_all_card(tg_id)
    return "succes"
