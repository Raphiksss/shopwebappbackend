from fastapi import APIRouter, Depends

from api_v1.schemas.settings import AssentColor
from api_v1.services.auth import check_if_auth
from api_v1.services.settings import change_accent_color,get_accent_color
from api_v1.schemas.general import ErrorResponse

router = APIRouter(tags=["Settings"])

@router.post("/accent_color/",summary="Set accent color",responses={
    401:{"model":ErrorResponse,"description":"Не авторизован"}
})
async def set_accent_color(color:AssentColor,_=Depends(check_if_auth)):
    return change_accent_color(color.color)

@router.get("/accent_color/",summary="Get accent color")
async def  accent_color():
    return get_accent_color()