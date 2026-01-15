from fastapi import APIRouter

from app.api.routes import router as organization_router


router = APIRouter()

router.include_router(organization_router)
