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
from app.repositories.activity import ActivityRepository
from app.repositories.building import BuildingRepository

from app.repositories.organization import OrganizationRepository
from app.repositories.organization_activity import OrganizationActivityRepository
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
    organization_activity_repository: ClassVar[OrganizationActivityRepository] = (
        get_repository(OrganizationActivityRepository)
    )
    phone_repository: ClassVar[PhoneRepository] = get_repository(PhoneRepository)
    building_repository: ClassVar[BuildingRepository] = get_repository(
        BuildingRepository
    )

    async def get_organizations(
        self,
        filters: OrganizationFilterSchema,
    ) -> OrganizationsListResponse:
        """Главный метод для получения организаций по фильтрам"""

        organization_ids = await self._intersection_organization_ids(
            filters=filters,
        )
        if organization_ids == self._empty_organization_response:
            return self._empty_organization_response

        return await self._get_organizations(
            filters=filters,
            organization_ids=organization_ids,
        )

    def _validate_radius_filters(
        self,
        filters: OrganizationFilterSchema,
    ) -> None:
        """Проверить наличие всех полей для поиска по радиусу."""

        if not (filters.radius and filters.latitude and filters.longitude):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Для поиска по радиусу необходимо указать latitude, longitude и radius",
            )

    async def _get_organizations(
        self,
        filters: OrganizationFilterSchema,
        organization_ids: list[int] | None = None,
    ) -> OrganizationsListResponse:
        """Общий метод для получения организаций с формированием ответа."""
        organizations = await self.organization_repository.get_organizations(
            filters=filters,
            organization_ids=organization_ids,
        )

        if not organizations:
            return self._empty_organization_response

        organization_ids = [organization.id for organization, _ in organizations]

        organization_activities_map, organization_phone_map = (
            await self._get_organizations_activities_and_phones_map(
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
        """Получить организацию по идентификатору."""

        organizations = await self._get_organizations(
            filters=OrganizationFilterSchema(),
            organization_ids=[organization_id],
        )

        if not organizations.results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found",
            )
        return organizations.results[0]

    async def _get_organization_ids_by_building_radius(
        self,
        latitude: float,
        longitude: float,
        radius: float,
    ) -> list[int]:
        """Получить ID зданий в радиусе от точки."""

        buildings = await self.building_repository.get_buildings_in_radius(
            latitude=latitude,
            longitude=longitude,
            radius=radius,
        )

        building_ids = [building.id for building in buildings]

        organizations = (
            await self.organization_repository.get_organization_by_building_ids(
                building_ids=building_ids,
            )
        )

        return [organization.id for organization in organizations]

    async def _get_organizations_activities_and_phones_map(
        self,
        organization_ids: list[int],
    ) -> tuple[dict, dict]:
        """Получить мапу активностей и мапу телефонов одновременно"""

        return await asyncio.gather(
            self.activity_repository.get_organizations_activities_map(organization_ids),
            self.phone_repository.get_organizations_phones_map(organization_ids),
        )

    @property
    def _empty_organization_response(
        self,
    ) -> OrganizationsListResponse:
        """Получить пустой ответ списка организаций."""

        return OrganizationsListResponse(results=[])

    async def _intersection_organization_ids(
        self,
        filters: OrganizationFilterSchema,
    ) -> list[int] | OrganizationsListResponse:
        """Ищем пересечения всех org_id из фильтров."""

        # Начинаем с None - значит пока нет фильтров
        organization_ids = None

        # 1. Если есть явные organization_ids
        if filters.organization_ids:
            organization_ids = set(filters.organization_ids_list)

        # 2. Если есть фильтр по активности
        if filters.activity_ids:
            organizations_by_activity = await self.organization_activity_repository.get_organization_ids_by_activity(
                activity_ids=filters.activity_ids_list,
            )

            activity_set = set(organizations_by_activity)
            if not activity_set:
                return self._empty_organization_response
            if organization_ids is not None:
                # Пересекаем с существующим
                organization_ids = organization_ids.intersection(activity_set)
            else:
                # Первый фильтр
                organization_ids = activity_set

        # 3. Если есть фильтр по радиусу
        if filters.radius or filters.latitude or filters.longitude:
            self._validate_radius_filters(filters=filters)
            organizations_by_radius = (
                await self._get_organization_ids_by_building_radius(
                    radius=filters.radius,
                    latitude=filters.latitude,
                    longitude=filters.longitude,
                )
            )

            radius_set = set(organizations_by_radius)
            if not radius_set:
                return self._empty_organization_response

            if organization_ids is not None:
                # Пересекаем с существующим
                organization_ids = organization_ids.intersection(radius_set)
            else:
                # Первый фильтр
                organization_ids = radius_set

        if filters.activity_search_str:
            organizations_by_activity_search = await self.organization_activity_repository.get_organization_ids_by_activity_search(
                activity_search_str=filters.activity_search_str,
            )

            activity_search_set = set(organizations_by_activity_search)
            if not activity_search_set:
                return self._empty_organization_response

            if organization_ids is not None:
                # Пересекаем с существующим
                organization_ids = organization_ids.intersection(activity_search_set)
            else:
                # Первый фильтр
                organization_ids = activity_search_set

        if organization_ids is not None and len(organization_ids) == 0:
            # Фильтры были, но пересечение пустое
            return self._empty_organization_response

        return list(organization_ids) if organization_ids is not None else None
