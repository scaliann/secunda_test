from fastapi import APIRouter, Depends, status

from app.api.filters.organization import OrganizationFilterSchema
from app.api.responses.organization import (
    OrganizationsListResponse,
    OrganizationResponse,
)
from app.authentication import check_permission
from app.services.organization import OrganizationService

organization_router = APIRouter(
    tags=["Organizations"],
    dependencies=[Depends(check_permission)],
)


@organization_router.get(
    path="/organizations",
    name="Get organizations list",
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


@organization_router.get(
    path="/organizations/{organization_id}",
    name="Get organization detail",
    status_code=status.HTTP_200_OK,
    response_model=OrganizationResponse,
)
async def get_organization(
    organization_id: int,
    service: OrganizationService = Depends(),
) -> OrganizationResponse:
    """Получить детальную информацию об организации."""

    return await service.get_organization(
        organization_id=organization_id,
    )
