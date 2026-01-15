from fastapi import APIRouter, Depends, status

from app.api.filters.organization import OrganizationFilterSchema
from app.api.responses.organization import (
    OrganizationsListResponse,
    OrganizationResponse,
)
from app.services.organization import OrganizationService

organization_router = APIRouter(tags=["Organizations"])


@organization_router.get(
    path="/organizations/buildings/{building_id}",
    response_model=OrganizationsListResponse,
    name="Get organizations",
    status_code=status.HTTP_200_OK,
    # response_model=OrganizationsListResponse,
)
async def get_organizations(
    building_id: int,
    service: OrganizationService = Depends(),
):
    return await service.get_organizations_by_building(building_id)


@organization_router.get(
    path="/organizations/{organization_id}",
    name="Get organization",
    status_code=status.HTTP_200_OK,
    # response_model=OrganizationResponse,
)
async def get_organizations(
    organization_id: int,
    service: OrganizationService = Depends(),
):

    return await service.get_organization(
        organization_id=organization_id,
    )
