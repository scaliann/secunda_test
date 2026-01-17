from fastapi import FastAPI

from app.router import router

SERVICE_URL_PREFIX = "/api"


app = FastAPI()

app.include_router(
    router,
    prefix=SERVICE_URL_PREFIX,
)


@app.get("/health")
async def health():
    return {"result": "success"}
