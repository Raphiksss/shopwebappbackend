from core.models import Admin
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import Request, HTTPException

async def create_admin(username:str,password:str, session: AsyncSession):
    new_admin = Admin(username=username, password = password)
    session.add(new_admin)
    await session.commit()
    return new_admin

async def check_admin(username:str, password:str, session: AsyncSession):
    stmt = select(Admin).where(Admin.username==username)
    res = await session.execute(stmt)
    admin =res.scalar_one_or_none()
    if not admin:
        return False
    if admin.password == password:
        return admin
    else:
        return False

async def check_if_auth(request: Request):
    admin_id = request.session.get("admin_id")
    if not admin_id:
        return False
    return True