import redis
import os

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

def add_product(tg_id:int, prod_id:int):
    with redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0) as r:
        r.json().set(f"card:{tg_id}", "$", {"products": {}}, nx = True)
        r.json().set(f"card:{tg_id}",f"$.products.{prod_id}",0, nx = True)
        r.json().numincrby(f"card:{tg_id}", f"$.products.{prod_id}",1)

def del_product(tg_id:int, prod_id: int):
    with redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0) as r:
        arr = r.json().get(f"card:{tg_id}", "$.products")[0]
        if arr.get(f'{prod_id}') == 1:
            r.json().delete(f"card:{tg_id}", f"$.products.{prod_id}")
        else:
            r.json().numincrby(f"card:{tg_id}", f"$.products.{prod_id}", -1)


def get_card(tg_id: int):
    with redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0) as r:
        result = r.json().get(f"card:{tg_id}")
        return result

