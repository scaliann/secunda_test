from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.router import router
from app.utils.seed_test_data import init_db

SERVICE_URL_PREFIX = "/api"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Инициализируем бд
    await init_db()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(
    router,
    prefix=SERVICE_URL_PREFIX,
)


@app.get("/health")
async def health():
    return {"result": "success"}
