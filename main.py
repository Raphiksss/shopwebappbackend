from contextlib import asynccontextmanager
from fastapi import FastAPI
import uvicorn
from core import settings, db_helper
from core.models import Base




app = FastAPI()

@app.router.get('/')
async def Hello():
    return('Hello')

if __name__ == '__main__':
    uvicorn.run(app, host = settings.host, port = settings.port)

