from dataclasses import dataclass, asdict
from datetime import datetime, timezone, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import Request, HTTPException
from pydantic import SecretStr
from aiogram.utils.web_app import safe_parse_webapp_init_data
import bcrypt

from api_v1.repositories.jwt_token_service import PyJWTTokenService
from api_v1.repositories.users import UserBy
from api_v1.services.users import get_user
from core import settings
from core.models import Admin, User

@dataclass(slots=True, frozen=True)
class AccessPayload:
    sub: str
    username: str
    iat: datetime
    exp: datetime


class ClientAuthService:
    def __init__(self, token_service: PyJWTTokenService,
                 session: AsyncSession,
                 access_til_days: int):
        self._token_service = token_service
        self._session = session
        self._access_til_days = access_til_days


    async def login(self, data: str) -> str:
        try:
            data = safe_parse_webapp_init_data(token=settings.BOT.bot_token, init_data=data)
        except ValueError:
            raise HTTPException(status_code=401, detail="Invalid init data")

        if datetime.now(timezone.utc) - data.auth_date > timedelta(hours=1):
            raise HTTPException(status_code=401, detail="Init data expired")

        tg_id = data.user.id
        user: User = await get_user(self._session, UserBy.TG_ID, tg_id)

        now = datetime.now(timezone.utc)
        exp = now + timedelta(days=self._access_til_days)

        payload = AccessPayload(str(user.tg_id), user.username, now, exp)
        access_token = self._token_service.encode(asdict(payload))

        return access_token

    async def get_user_data(self, encoded_payload: str) -> AccessPayload:
        return AccessPayload(**self._token_service.decode(encoded_payload))



