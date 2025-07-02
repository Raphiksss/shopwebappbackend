import asyncio
import logging
import threading
from contextlib import asynccontextmanager
from fastapi import FastAPI
import uvicorn
from bot import bot, dp
from core import settings
from api_products import router
from core import configure_logging
from fastapi.middleware.cors import CORSMiddleware
from api_users import router as users_router


logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    def _start():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(
            dp.start_polling(
                bot,
                skip_updates=True,
                handle_signals=False
            )
        )
    t = threading.Thread(target=_start, daemon=True)
    t.start()
    yield


app = FastAPI(lifespan = lifespan)
app.include_router(router)
app.include_router(users_router)
app.add_middleware(CORSMiddleware,allow_origins=settings.origins,allow_credentials=False,allow_methods=["*"],allow_headers=["*"],)


@app.get('/')
async def hello():
    return 'Hello'

if __name__ == '__main__':
    configure_logging()
    uvicorn.run(app, host = settings.host, port = settings.port)

