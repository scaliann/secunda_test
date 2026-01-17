from app.models.phone import Phone
from app.repositories.base import Repository
import sqlalchemy as sa


class PhoneRepository(Repository):
    model = Phone

    async def get_organizations_phones_map(
        self,
        organization_ids: list[int],
    ) -> dict[int, str]:
        """Получить мапу организаций и их телефонов"""

        if not organization_ids:
            return {}

        query = sa.select(
            Phone.phone_number,
            Phone.organization_id,
        ).where(
            Phone.organization_id.in_(
                organization_ids,
            ),
        )

        result = await self.session.execute(query)
        rows = result.fetchall()

        phone_map = {}
        for row in rows:
            organization_id = row.organization_id

            if organization_id not in phone_map:
                phone_map[organization_id] = []

            phone_map[organization_id].append(row.phone_number)

        return phone_map
