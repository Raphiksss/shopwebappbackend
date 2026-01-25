from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.ext.asyncio.session import AsyncSession
from core.db_helper import get_session
from ..services import auth

router = APIRouter(prefix='',tags=["Auth"])


@router.post("/admin/", summary = "создать админа")
async def create_admin(username:str, password:str,session:AsyncSession = Depends(get_session), chk:bool = Depends(auth.check_if_auth)):
    if not chk:
        raise HTTPException(status_code=401,detail="Not authenticated")
    res = await auth.create_admin(username,password,session)
    return res

@router.get("/login/", summary = "залогиниться")
async def admin_auth(request: Request, username:str, password:str,session:AsyncSession = Depends(get_session)):
    admin = await auth.check_admin(username, password, session)
    if not admin:
        raise HTTPException(status_code=401,detail = "Invalid Credentials")
    request.session["admin_id"] = admin.id
    return {"status": "ok", "message": "Logged in successfully"}

@router.get("/me/", summary="Текущий админ")
async def get_me(request: Request, chk:bool = Depends(auth.check_if_auth)):
    if not chk:
        raise HTTPException(status_code=401,detail="Not authenticated")
    return {
        "admin_id": request.session.get("admin_id"),
    }