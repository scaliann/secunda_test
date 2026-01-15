from fastapi import APIRouter

from app.api.routes.organization import organization_router

router_v1 = APIRouter(prefix="/v1")

router_v1.include_router(organization_router)


router = APIRouter()
router.include_router(router_v1)
