import asyncio
import threading
from contextlib import asynccontextmanager
from fastapi import FastAPI
import uvicorn
from bot import run_polling
from core import settings, db_helper
from api_products import router
import logging

logger = logging.getLogger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    def start_bot_loop():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(run_polling())
    t = threading.Thread(target=start_bot_loop, daemon=True)
    t.start()
    logger.warning("Бот запущен")

    yield

app = FastAPI(lifespan = lifespan)
app.include_router(router)

@app.get('/')
async def hello():
    return 'Hello'

if __name__ == '__main__':
    uvicorn.run(app, host = settings.host, port = settings.port)

