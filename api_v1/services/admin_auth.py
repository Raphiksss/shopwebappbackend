import bcrypt
from fastapi import HTTPException, Request
from pydantic import SecretStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.models import Admin


def validate_password(password: str, hashed: bytes) -> bool:
    pb = password.encode()
    return bcrypt.checkpw(pb, hashed)

async def hash_password(password: str) -> bytes:
    salt = bcrypt.gensalt()
    pb = password.encode()
    return bcrypt.hashpw(pb, salt)

async def create_admin(username: str | SecretStr, password: str, session: AsyncSession):
    hashed_password: bytes = await hash_password(password)
    new_admin = Admin(username=username, password=hashed_password)
    session.add(new_admin)
    await session.commit()
    return new_admin


async def check_admin(username: str, password: str, session: AsyncSession):
    stmt = select(Admin).where(Admin.username == username)
    res = await session.execute(stmt)
    admin = res.scalar_one_or_none()
    if not admin:
        raise HTTPException(status_code=403, detail="Admin not found")
    p_c = validate_password(password, admin.password)
    if not p_c:
        raise HTTPException(status_code=403, detail="Invalid credentials")
    return admin


async def check_if_auth(request: Request):
    admin_id = request.session.get("admin_id")
    if not admin_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return admin_id


async def logout(request: Request):
    request.session.pop("admin_id")
    return None