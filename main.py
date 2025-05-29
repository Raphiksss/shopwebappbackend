from fastapi import FastAPI
import uvicorn
from core import settings

app = FastAPI()

@app.router.get('/')
async def Hello():
    return('Hello')


uvicorn.run(app, host = settings.host, port = settings.port)