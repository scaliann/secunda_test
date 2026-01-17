from app.models.activity import Activity
from app.models.organization_activity import OrganizationActivity
from app.repositories.base import Repository
import sqlalchemy as sa


class OrganizationActivityRepository(Repository):
    model = OrganizationActivity

    async def get_organization_ids_by_activity(
        self,
        activity_ids: list[int],
    ) -> list[int]:
        """Получить ID организаций по конкретной деятельности"""

        query = sa.select(
            OrganizationActivity.organization_id,
        ).where(
            OrganizationActivity.activity_id.in_(activity_ids),
        )

        result = await self.session.execute(query)
        organization_ids = result.scalars().all()
        return list(set(organization_ids))

    async def get_organization_ids_by_activity_search(
        self,
        activity_search_str: str,
    ) -> list[int]:
        """Получить ID организаций по конкретной деятельности"""

        query = (
            sa.select(
                OrganizationActivity.organization_id,
            )
            .join(
                Activity,
                Activity.id == self.model.activity_id,
            )
            .where(
                Activity.name.ilike(
                    f"%{activity_search_str}%",
                ),
            )
        )
        result = await self.session.execute(query)
        organization_ids = result.scalars().all()

        return list(set(organization_ids))
