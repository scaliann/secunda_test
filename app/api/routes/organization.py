from fastapi import APIRouter, Depends, status

from app.api.filters.organization import OrganizationFilterSchema
from app.api.responses.organization import (
    OrganizationsListResponse,
)
from app.authentication import check_permission
from app.services.organization import OrganizationService

organization_router = APIRouter(
    tags=["Organizations"],
    dependencies=[Depends(check_permission)],
)


@organization_router.get(
    path="/organizations",
    name="Get organizations",
    status_code=status.HTTP_200_OK,
    response_model=OrganizationsListResponse,
)
async def get_organizations(
    filters: OrganizationFilterSchema = Depends(),
    service: OrganizationService = Depends(),
) -> OrganizationsListResponse:
    """Получить организации."""

    return await service.get_organizations(
        filters=filters,
    )
