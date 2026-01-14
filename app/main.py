from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.utils.seed_test_data import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Инициализируем бд
    await init_db()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/health")
async def health():
    return {"result": "success"}
