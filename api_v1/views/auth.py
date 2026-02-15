from fastapi import APIRouter, Request, HTTPException, Depends, Form
from sqlalchemy.ext.asyncio.session import AsyncSession
from core.db_helper import get_session
from ..services import auth

router = APIRouter(prefix='',tags=["Auth"])


@router.post("/admin/", summary = "Create new admin")
async def create_admin(username:str= Form(...), password:str= Form(...),session:AsyncSession = Depends(get_session), _=Depends(auth.check_if_auth)):
    res = await auth.create_admin(username,password,session)
    return res

@router.post("/login/", summary = "Authorisation")
async def admin_auth(request: Request, login:str = Form(...),password:str = Form(...),session:AsyncSession = Depends(get_session)):
    admin = await auth.check_admin(login, password, session)
    if not admin:
        raise HTTPException(status_code=403,detail = "Invalid Credentials")
    request.session["admin_id"] = admin.id
    return {"status": "ok", "message": "Logged in successfully"}

@router.get("/me/", summary="Get current admin")
async def get_me(admin_id:str = Depends(auth.check_if_auth)):
    return {
        "admin_id": admin_id,
    }
@router.delete("/logout/", summary="Logout")
async def logout(request:Request, _=Depends(auth.check_if_auth)):
    await auth.logout(request)
    return None