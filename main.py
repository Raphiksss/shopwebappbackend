import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
import uvicorn
from bot.bot import bt, dp
from bot.consumers import start_consumers, stop_consumers
from core import settings
from core import logger
from core.rabbitmq import broker
from fastapi.middleware.cors import CORSMiddleware
from api_v1 import router as v1_router
from starlette.middleware.sessions import SessionMiddleware



@asynccontextmanager
async def lifespan(app: FastAPI):
    # Запускаем RabbitMQ broker для API (producer)
    await broker.start()
    logger.info("RabbitMQ broker started")

    # Запускаем RabbitMQ consumers (обработчики очередей)
    await start_consumers()
    logger.info("RabbitMQ consumers started")

    # Запускаем Telegram bot как asyncio Task
    bot_task = asyncio.create_task(
        dp.start_polling(bt, skip_updates=True)
    )
    logger.info("Telegram bot started as asyncio task")

    yield

    # Graceful shutdown всех сервисов
    logger.info("Shutting down services...")

    # Останавливаем бота
    logger.info("Shutting down Telegram bot...")
    bot_task.cancel()
    try:
        await bot_task
    except asyncio.CancelledError:
        logger.info("Bot task cancelled successfully")

    await bt.session.close()
    logger.info("Bot session closed")

    # Останавливаем RabbitMQ consumers
    await stop_consumers()
    logger.info("RabbitMQ consumers stopped")

    # Останавливаем RabbitMQ broker
    await broker.close()
    logger.info("RabbitMQ broker stopped")


app = FastAPI(lifespan = lifespan)

app.include_router(v1_router)
app.add_middleware(CORSMiddleware,allow_origins=settings.origins,allow_credentials=True,allow_methods=["*"],allow_headers=["*"],)
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_SESSION_KEY,max_age = settings.SESSION_EXPIRE_TIME)

@app.get('/')
async def hello():
    return 'Hello'

if __name__ == '__main__':
    uvicorn.run(app, host = settings.host, port = settings.port)

