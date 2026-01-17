from app.models.activity import Activity
from app.models.organization_activity import OrganizationActivity
from app.repositories.base import Repository
import sqlalchemy as sa


class ActivityRepository(Repository):
    model = Activity

    async def get_organizations_activities_map(
        self,
        organization_ids: list[int],
    ) -> dict[int, list[Activity]]:
        """Получить мапу организаций и их активностей"""

        if not organization_ids:
            return {}

        query = (
            sa.select(
                OrganizationActivity.organization_id,
                Activity.id,
                Activity.name,
                Activity.parent_id,
            )
            .join(
                OrganizationActivity,
                OrganizationActivity.activity_id == Activity.id,
            )
            .where(
                OrganizationActivity.organization_id.in_(
                    organization_ids,
                ),
            )
            .order_by(
                OrganizationActivity.organization_id,
                Activity.name,
            )
        )

        result = await self.session.execute(query)
        rows = result.fetchall()

        activities_map = {}
        for row in rows:
            organization_id = row.organization_id

            if organization_id not in activities_map:
                activities_map[organization_id] = []

            activities_map[organization_id].append(
                Activity(
                    id=row.id,
                    name=row.name,
                    parent_id=row.parent_id,
                )
            )

        return activities_map
