import redis
from fastapi import HTTPException
from core import settings

REDIS_HOST = settings.DB.REDIS_HOST
REDIS_PORT = settings.DB.REDIS_PORT


def change_accent_color(accent_color:str):
    with redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0) as r:
        r.set("accent_color", accent_color)
    return {"accent_color":accent_color}

def get_accent_color():
    with redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0) as r:
        accent_color = r.get("accent_color")
    return {"accent_color":accent_color}