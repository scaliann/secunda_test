import sqlalchemy as sa
from typing import List
from app.models.building import Building
from app.repositories.base import Repository


class BuildingRepository(Repository):
    model = Building

    async def get_buildings_in_radius(
        self,
        latitude: float,
        longitude: float,
        radius: float,
    ) -> List[Building]:
        """
        Найти здания в радиусе от точки (используя формулу гаверсинуса).
        """

        query = sa.text(
            """
                SELECT * FROM building 
                WHERE 6371 * acos(
                    cos(radians(:lat)) * cos(radians(latitude)) * 
                    cos(radians(longitude) - radians(:lon)) + 
                    sin(radians(:lat)) * sin(radians(latitude))
                ) <= :radius
            """
        )

        result = await self.session.execute(
            query,
            {
                "lat": latitude,
                "lon": longitude,
                "radius": radius,
            },
        )

        rows = result.fetchall()
        buildings = []
        for row in rows:
            building = Building(
                id=row.id,
                address=row.address,
                latitude=row.latitude,
                longitude=row.longitude,
            )
            buildings.append(building)

        return buildings
