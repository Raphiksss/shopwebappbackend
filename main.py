import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from bot.bot import run_polling
from bot.consumers import start_consumers, stop_consumers
from core import settings
from core import logger
from core.rabbitmq import broker
from fastapi.middleware.cors import CORSMiddleware
from api_v1 import router as v1_router
from starlette.middleware.sessions import SessionMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):

    await broker.start()
    logger.info("RabbitMQ broker started")

    await start_consumers()
    logger.info("RabbitMQ consumers started")

    bot_task = asyncio.create_task(run_polling())
    logger.info("Telegram bot started as asyncio task")

    yield

    logger.info("Shutting down services...")

    logger.info("Shutting down Telegram bot...")
    bot_task.cancel()
    try:
        await bot_task
    except asyncio.CancelledError:
        logger.info("Bot task cancelled successfully")

    await stop_consumers()
    logger.info("RabbitMQ consumers stopped")

    await broker.close()
    logger.info("RabbitMQ broker stopped")


app = FastAPI(lifespan=lifespan)

app.include_router(v1_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_SESSION_KEY,
    max_age=settings.SESSION_EXPIRE_TIME,
    https_only=settings.SESSION_SECURE,
)


@app.get("/")
async def hello():
    return "Hello"
