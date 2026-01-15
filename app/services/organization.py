import asyncio
from dataclasses import dataclass
from typing import ClassVar

from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.api.filters.organization import OrganizationFilterSchema
from app.api.responses.building import BuildingResponse
from app.api.responses.organization import (
    OrganizationsListResponse,
    OrganizationResponse,
    ActivityResponse,
)
from app.database import get_session
from app.models.activity import Activity
from app.models.organization import Organization
from app.repositories.activity import ActivityRepository

from app.repositories.organization import OrganizationRepository
from app.repositories.phone import PhoneRepository
from app.services.base import get_repository


@dataclass
class OrganizationService:
    session: AsyncSession = Depends(get_session)
    organization_repository: ClassVar[OrganizationRepository] = get_repository(
        OrganizationRepository
    )
    activity_repository: ClassVar[ActivityRepository] = get_repository(
        ActivityRepository
    )
    phone_repository: ClassVar[PhoneRepository] = get_repository(PhoneRepository)

    async def get_organizations_by_building(
        self,
        building_id: int,
    ) -> OrganizationsListResponse:
        """Получить организации по конкретному зданию."""

        organizations = await self.organization_repository.get_organizations(
            building_ids=[building_id],
        )

        if not organizations:
            return OrganizationsListResponse(
                results=[],
            )

        organization_ids = [organization.id for organization, _ in organizations]

        organization_activities_map, organization_phone_map = (
            await self.get_organizations_activities_and_phones_map(
                organization_ids,
            )
        )

        results = []

        for organization, building in organizations:
            results.append(
                OrganizationResponse(
                    id=organization.id,
                    name=organization.name,
                    building=BuildingResponse(
                        id=building.id,
                        address=building.address,
                        latitude=building.latitude,
                        longitude=building.longitude,
                    ),
                    activities=(
                        [
                            ActivityResponse(
                                id=activity.id,
                                name=activity.name,
                                parent_id=activity.parent_id,
                            )
                            for activity in organization_activities_map[organization.id]
                        ]
                        if organization_activities_map.get(organization.id, None)
                        else None
                    ),
                    phones=(
                        [
                            phone_number
                            for phone_number in organization_phone_map[organization.id]
                        ]
                        if organization_phone_map.get(organization.id, None)
                        else None
                    ),
                )
            )

        return OrganizationsListResponse(
            results=results,
        )

    async def get_organization(
        self,
        organization_id: int,
    ) -> OrganizationResponse:

        organization = await self.organization_repository.get_organizations(
            organization_ids=[organization_id],
        )
        if not organization:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found",
            )

        organization_activities_map, organization_phone_map = (
            await self.get_organizations_activities_and_phones_map(
                [organization_id],
            )
        )

        organization, building = organization[0]

        return OrganizationResponse(
            id=organization.id,
            name=organization.name,
            building=BuildingResponse(
                id=building.id,
                address=building.address,
                latitude=building.latitude,
                longitude=building.longitude,
            ),
            activities=(
                [
                    ActivityResponse(
                        id=activity.id, name=activity.name, parent_id=activity.parent_id
                    )
                    for activity in organization_activities_map[organization.id]
                ]
                if organization_activities_map
                else None
            ),
            phones=(
                [
                    phone_number
                    for phone_number in organization_phone_map[organization.id]
                ]
                if organization_phone_map
                else None
            ),
        )

    async def get_organizations_activities_and_phones_map(
        self, organization_ids: list[int]
    ) -> tuple[dict, dict]:
        """Получить две мапы одновременно"""

        return await asyncio.gather(
            self.activity_repository.get_organizations_activities_map(organization_ids),
            self.phone_repository.get_organizations_phones_map(organization_ids),
        )
