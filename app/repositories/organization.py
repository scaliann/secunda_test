from app.api.filters.organization import OrganizationFilterSchema
from app.models.building import Building
from app.models.organization import Organization
from app.repositories.base import Repository
import sqlalchemy as sa


class OrganizationRepository(Repository):
    model = Organization

    async def get_organizations(
        self,
        filters: OrganizationFilterSchema,
        organization_ids: list[int] | None = None,
    ) -> list[tuple[Organization, Building]]:
        """Получить организации по фильтрам."""

        query = sa.select(
            Organization,
            Building,
        ).join(
            Building,
            self.model.building_id == Building.id,
        )

        if filters.building_ids:
            query = query.where(
                self.model.building_id.in_(
                    filters.building_ids,
                ),
            )

        if organization_ids:
            query = query.where(
                self.model.id.in_(
                    organization_ids,
                )
            )

        if filters.search_str:
            query = query.where(self.model.name.ilike(f"%{filters.search_str}%"))

        result = await self.session.execute(query)

        return result.all()

    async def get_organization_by_building_ids(
        self,
        building_ids: list[int] | None,
    ) -> list[Organization]:
        """Получить организации по building_ids"""

        query = sa.select(
            Organization,
        ).where(
            self.model.building_id.in_(
                building_ids,
            )
        )

        result = await self.session.execute(query)
        return list(result.scalars().all())
