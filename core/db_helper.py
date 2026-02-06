from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import sessionmaker

from .config import settings

engine: AsyncEngine = create_async_engine(
    settings.DB.db_url,
    connect_args={
        "server_settings": {"jit": "off"},
        "ssl": False
    }
)
AsyncSessionLocal = async_sessionmaker(
    bind = engine,
    class_ = AsyncSession,
    expire_on_commit = False
)
async def get_session() ->AsyncGenerator[AsyncSession,None]  :
    async with AsyncSessionLocal() as session:
        yield session

