from fastapi import FastAPI
import uvicorn
from core import settings

app = FastAPI()

@app.router.get('/')
async def Hello():
    return('Hello')

if __name__ == '__main__':
    uvicorn.run(app, host = settings.host, port = settings.port)

