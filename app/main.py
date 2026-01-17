from fastapi import FastAPI

from app.router import router

SERVICE_URL_PREFIX = "/api"


app = FastAPI(
    title="Справочник организаций",
    summary="Тестовое задание для REST API приложения.",
    version="1.0.0",
    contact={
        "name": "Малодушев Михаил",
        "url": "https://t.me/scaliann",
    },
)

app.include_router(
    router,
    prefix=SERVICE_URL_PREFIX,
)


@app.get("/health")
async def health():
    return {"result": "success"}
