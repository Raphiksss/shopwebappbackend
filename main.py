from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.router.get('/')
async def Hello():
    return('Hello')


uvicorn.run(app)