import redis
from fastapi import HTTPException
from core import settings

REDIS_HOST = settings.DB.REDIS_HOST
REDIS_PORT = settings.DB.REDIS_PORT

def add_product(tg_id:int, prod_id:int):
    with redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0) as r:
        r.json().set(f"card:{tg_id}", "$", {"products": {}}, nx = True)
        r.json().set(f"card:{tg_id}",f"$.products.{prod_id}",0, nx = True)
        r.json().numincrby(f"card:{tg_id}", f"$.products.{prod_id}",1)
    return r.json().get(f"card:{tg_id}")

def del_product(tg_id:int, prod_id: int):
    with redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0) as r:
        arr = r.json().get(f"card:{tg_id}", "$.products")[0]
        cnt = arr.get(f'{prod_id}')
        if not cnt:
            raise HTTPException(status_code=404, detail="Товар отсутствует в корзине ")
        elif cnt == 1:
            r.json().delete(f"card:{tg_id}", f"$.products.{prod_id}")
        else:
            r.json().numincrby(f"card:{tg_id}", f"$.products.{prod_id}", -1)
    return None

def del_all_one_product(tg_id:int, prod_id: int):
    with redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0) as r:
        r.json().delete(f"card:{tg_id}", f"$.products.{prod_id}")
    return None


def del_all_card(tg_id: int):
    with redis.Redis(host = REDIS_HOST, port = REDIS_PORT, db = 0) as r:
        r.json().set(f"card:{tg_id}","$.products",{})
    return None

def get_card(tg_id: int):
    with redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0) as r:
        result = r.json().get(f"card:{tg_id}")
    return result

