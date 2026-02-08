from core.models import Admin
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import Request, HTTPException
from pydantic import SecretStr,BaseModel
import bcrypt

class Login(BaseModel):
    username:str
    password:str


async def hash_password(password:str) -> bytes:
    salt = bcrypt.gensalt()
    pb = password.encode()
    return bcrypt.hashpw(pb, salt)

def validate_password(password: str, hashed: bytes) -> bool:
    pb = password.encode()
    return bcrypt.checkpw(pb, hashed)

async def create_admin(username:str|SecretStr,password:str, session: AsyncSession):
    hashed_password:bytes = await hash_password(password)
    new_admin = Admin(username=username, password = hashed_password)
    session.add(new_admin)
    await session.commit()
    return new_admin

async def check_admin(username:str, password:str, session: AsyncSession):
    stmt = select(Admin).where(Admin.username==username)
    res = await session.execute(stmt)
    admin = res.scalar_one_or_none()
    if not admin:
        raise HTTPException(status_code=403,detail="Admin not found")
    p_c = validate_password(password, admin.password)
    if not p_c:
        raise HTTPException(status_code=403, detail="Invalid credentials")
    return admin

async def check_if_auth(request: Request):
    admin_id = request.session.get("admin_id")
    if not admin_id:
        return False
    return True