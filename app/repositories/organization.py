from sqlalchemy.orm import selectinload, aliased

from app.api.filters.organization import OrganizationFilterSchema
from app.models.activity import Activity
from app.models.building import Building
from app.models.organization import Organization
from app.models.organization_activity import OrganizationActivity
from app.models.phone import Phone
from app.repositories.base import Repository
import sqlalchemy as sa


class OrganizationRepository(Repository):
    model = Organization

    async def get_organizations(
        self,
        building_ids: list[int] | None = None,
        organization_ids: list[int] | None = None,
    ) -> list[tuple[Organization, Building]]:
        """
        Получить организации по фильтрам.
        """

        query = sa.select(
            Organization,
            Building,
        ).join(
            Building,
            self.model.building_id == Building.id,
        )

        if building_ids:
            query = query.where(
                self.model.building_id.in_(
                    building_ids,
                ),
            )

        if organization_ids:
            query = query.where(
                self.model.id.in_(
                    organization_ids,
                )
            )

        result = await self.session.execute(query)

        return result.all()
