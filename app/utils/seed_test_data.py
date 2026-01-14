from sqlalchemy import select, insert, func

from app.database import get_session, async_engine
from app.models.activity import Activity
from app.models.base import Base
from app.models.building import Building
from app.models.organization import Organization
from app.models.organization_activity import OrganizationActivity
from app.models.phone import Phone


async def init_db() -> None:
    """Создать таблицы и заполнить их."""

    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await seed_test_data()


async def seed_test_data() -> None:
    """Заполнить таблицы тестовыми данными."""

    async with get_session() as session:
        count_query = select(func.count()).select_from(Organization)

        if await session.scalar(count_query) > 0:
            return

        # 1. Здания
        buildings_query = (
            insert(Building)
            .values(
                [
                    {
                        "address": "г. Москва, ул. Тверская 1, офис 101",
                        "latitude": 55.7600,
                        "longitude": 37.6175,
                    },
                    {
                        "address": "г. Москва, ул. Арбат 25",
                        "latitude": 55.7500,
                        "longitude": 37.5914,
                    },
                    {
                        "address": "г. Санкт-Петербург, Невский пр. 28",
                        "latitude": 59.9358,
                        "longitude": 30.3259,
                    },
                    {
                        "address": "г. Екатеринбург, ул. Блюхера 32/1",
                        "latitude": 56.8389,
                        "longitude": 60.6057,
                    },
                    {
                        "address": "г. Казань, ул. Баумана 35",
                        "latitude": 55.7961,
                        "longitude": 49.1064,
                    },
                ]
            )
            .returning(Building.id)
        )

        building_result = await session.execute(buildings_query)
        building_ids = [r[0] for r in building_result.fetchall()]

        # 2. Деятельности

        activities_query = (
            insert(Activity)
            .values(
                [
                    {"name": "Еда", "parent_id": None},
                    {"name": "Автомобили", "parent_id": None},
                    {"name": "IT", "parent_id": None},
                    {"name": "Розничная торговля", "parent_id": None},
                    {"name": "Услуги", "parent_id": None},
                    {"name": "Мясная продукция", "parent_id": 1},
                    {"name": "Молочная продукция", "parent_id": 1},
                    {"name": "Хлебобулочные изделия", "parent_id": 1},
                    {"name": "Говядина", "parent_id": 6},
                    {"name": "Свинина", "parent_id": 6},
                    {"name": "Сыры", "parent_id": 7},
                    {"name": "Йогурты", "parent_id": 7},
                    {"name": "Хлеб", "parent_id": 8},
                    {"name": "Торты", "parent_id": 8},
                ]
            )
            .returning(Activity.id, Activity.name)
        )

        activities_result = await session.execute(activities_query)
        activities = {name: id for id, name in activities_result.fetchall()}

        # 3. Организации
        organization_query = (
            insert(Organization)
            .values(
                [
                    {"name": 'ООО "Рога и Копыта"', "building_id": building_ids[0]},
                    {"name": 'ИП "АвтоМир"', "building_id": building_ids[1]},
                    {"name": 'ЗАО "IT-Технологии"', "building_id": building_ids[2]},
                    {"name": 'ОАО "ВкусВилл"', "building_id": building_ids[3]},
                    {"name": 'ТОО "Уютный Дом"', "building_id": building_ids[4]},
                ]
            )
            .returning(Organization.id)
        )

        orgs_result = await session.execute(organization_query)
        org_ids = [r[0] for r in orgs_result.fetchall()]

        # 4. Связи организация-деятельность
        await session.execute(
            insert(OrganizationActivity).values(
                [
                    {
                        "organization_id": org_ids[0],
                        "activity_id": activities["Мясная продукция"],
                    },
                    {
                        "organization_id": org_ids[0],
                        "activity_id": activities["Молочная продукция"],
                    },
                    {
                        "organization_id": org_ids[1],
                        "activity_id": activities["Автомобили"],
                    },
                    {"organization_id": org_ids[2], "activity_id": activities["IT"]},
                    {"organization_id": org_ids[3], "activity_id": activities["Еда"]},
                    {
                        "organization_id": org_ids[3],
                        "activity_id": activities["Хлебобулочные изделия"],
                    },
                    {
                        "organization_id": org_ids[4],
                        "activity_id": activities["Розничная торговля"],
                    },
                    {
                        "organization_id": org_ids[4],
                        "activity_id": activities["Услуги"],
                    },
                ]
            )
        )

        # 5. Телефоны
        await session.execute(
            insert(Phone).values(
                [
                    {"organization_id": org_ids[0], "phone_number": "8-495-111-22-33"},
                    {"organization_id": org_ids[0], "phone_number": "8-495-222-33-44"},
                    {"organization_id": org_ids[1], "phone_number": "8-812-333-44-55"},
                    {"organization_id": org_ids[2], "phone_number": "8-343-444-55-66"},
                    {"organization_id": org_ids[2], "phone_number": "8-343-555-66-77"},
                    {"organization_id": org_ids[3], "phone_number": "8-843-666-77-88"},
                    {"organization_id": org_ids[4], "phone_number": "8-495-777-88-99"},
                    {"organization_id": org_ids[4], "phone_number": "8-495-888-99-00"},
                    {"organization_id": org_ids[4], "phone_number": "8-800-123-45-67"},
                ]
            )
        )

        await session.commit()
