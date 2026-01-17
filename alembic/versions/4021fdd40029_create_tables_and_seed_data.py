"""Create tables and seed data

Revision ID: 4021fdd40029
Revises:
Create Date: 2026-01-17 18:07:09.235980

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "4021fdd40029"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    # Таблица building
    op.create_table(
        "building",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("address", sa.String(), nullable=True),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    # Таблица activity
    op.create_table(
        "activity",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("parent_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["parent_id"],
            ["activity.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Таблица organization
    op.create_table(
        "organization",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("building_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["building_id"],
            ["building.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Таблица organization_activity (связь многие-ко-многим)
    op.create_table(
        "organization_activity",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=True),
        sa.Column("activity_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["activity_id"],
            ["activity.id"],
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organization.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Таблица phone
    op.create_table(
        "phone",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=True),
        sa.Column("phone_number", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organization.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # ========== 2. ЗАПОЛНЯЕМ ДАННЫЕ ==========

    # Создаем временные табличные объекты
    building = sa.table(
        "building",
        sa.column("id", sa.Integer),
        sa.column("address", sa.String),
        sa.column("latitude", sa.Float),
        sa.column("longitude", sa.Float),
    )

    activity = sa.table(
        "activity",
        sa.column("id", sa.Integer),
        sa.column("name", sa.String),
        sa.column("parent_id", sa.Integer),
    )

    organization = sa.table(
        "organization",
        sa.column("id", sa.Integer),
        sa.column("name", sa.String),
        sa.column("building_id", sa.Integer),
    )

    organization_activity = sa.table(
        "organization_activity",
        sa.column("id", sa.Integer),
        sa.column("organization_id", sa.Integer),
        sa.column("activity_id", sa.Integer),
    )

    phone = sa.table(
        "phone",
        sa.column("id", sa.Integer),
        sa.column("organization_id", sa.Integer),
        sa.column("phone_number", sa.String),
    )

    # 2.1 Вставляем здания через bulk_insert (возвращает ID)
    op.bulk_insert(
        building,
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
        ],
    )

    # 2.2 Вставляем родительские деятельности
    op.bulk_insert(
        activity,
        [
            {"name": "Еда", "parent_id": None},
            {"name": "Автомобили", "parent_id": None},
            {"name": "IT", "parent_id": None},
            {"name": "Розничная торговля", "parent_id": None},
            {"name": "Услуги", "parent_id": None},
        ],
    )

    # 2.3 Вставляем дочерние деятельности (используем raw SQL с подзапросами)
    connection = op.get_bind()

    # Получаем ID родительской "Еда"
    result = connection.execute(sa.text("SELECT id FROM activity WHERE name = 'Еда'"))
    food_id = result.fetchone()[0]

    # Вставляем дочерние
    op.bulk_insert(
        activity,
        [
            {"name": "Мясная продукция", "parent_id": food_id},
            {"name": "Молочная продукция", "parent_id": food_id},
            {"name": "Хлебобулочные изделия", "parent_id": food_id},
        ],
    )

    # Получаем ID для вставки внучатых
    result = connection.execute(
        sa.text("SELECT id, name FROM activity WHERE parent_id IS NOT NULL")
    )
    child_activities = {row[1]: row[0] for row in result.fetchall()}

    # Вставляем внучатые
    op.bulk_insert(
        activity,
        [
            {"name": "Говядина", "parent_id": child_activities["Мясная продукция"]},
            {"name": "Свинина", "parent_id": child_activities["Мясная продукция"]},
            {"name": "Сыры", "parent_id": child_activities["Молочная продукция"]},
            {"name": "Йогурты", "parent_id": child_activities["Молочная продукция"]},
            {"name": "Хлеб", "parent_id": child_activities["Хлебобулочные изделия"]},
            {"name": "Торты", "parent_id": child_activities["Хлебобулочные изделия"]},
        ],
    )

    # 2.4 Вставляем организации (связываем с зданиями)
    # Получаем ID зданий
    result = connection.execute(sa.text("SELECT id, address FROM building ORDER BY id"))
    buildings = {row[1]: row[0] for row in result.fetchall()}

    op.bulk_insert(
        organization,
        [
            {
                "name": 'ООО "Рога и Копыта"',
                "building_id": buildings["г. Москва, ул. Тверская 1, офис 101"],
            },
            {
                "name": 'ИП "АвтоМир"',
                "building_id": buildings["г. Москва, ул. Арбат 25"],
            },
            {
                "name": 'ЗАО "IT-Технологии"',
                "building_id": buildings["г. Санкт-Петербург, Невский пр. 28"],
            },
            {
                "name": 'ОАО "ВкусВилл"',
                "building_id": buildings["г. Екатеринбург, ул. Блюхера 32/1"],
            },
            {
                "name": 'ТОО "Уютный Дом"',
                "building_id": buildings["г. Казань, ул. Баумана 35"],
            },
        ],
    )

    # 2.5 Получаем ID для связей
    result = connection.execute(sa.text("SELECT id, name FROM activity"))
    activities = {row[1]: row[0] for row in result.fetchall()}

    result = connection.execute(sa.text("SELECT id, name FROM organization"))
    organizations = {row[1]: row[0] for row in result.fetchall()}

    # Вставляем связи организация-деятельность
    op.bulk_insert(
        organization_activity,
        [
            {
                "organization_id": organizations['ООО "Рога и Копыта"'],
                "activity_id": activities["Мясная продукция"],
            },
            {
                "organization_id": organizations['ООО "Рога и Копыта"'],
                "activity_id": activities["Молочная продукция"],
            },
            {
                "organization_id": organizations['ИП "АвтоМир"'],
                "activity_id": activities["Автомобили"],
            },
            {
                "organization_id": organizations['ЗАО "IT-Технологии"'],
                "activity_id": activities["IT"],
            },
            {
                "organization_id": organizations['ОАО "ВкусВилл"'],
                "activity_id": activities["Еда"],
            },
            {
                "organization_id": organizations['ОАО "ВкусВилл"'],
                "activity_id": activities["Хлебобулочные изделия"],
            },
            {
                "organization_id": organizations['ТОО "Уютный Дом"'],
                "activity_id": activities["Розничная торговля"],
            },
            {
                "organization_id": organizations['ТОО "Уютный Дом"'],
                "activity_id": activities["Услуги"],
            },
        ],
    )

    # 2.6 Вставляем телефоны
    op.bulk_insert(
        phone,
        [
            {
                "organization_id": organizations['ООО "Рога и Копыта"'],
                "phone_number": "8-495-111-22-33",
            },
            {
                "organization_id": organizations['ООО "Рога и Копыта"'],
                "phone_number": "8-495-222-33-44",
            },
            {
                "organization_id": organizations['ИП "АвтоМир"'],
                "phone_number": "8-812-333-44-55",
            },
            {
                "organization_id": organizations['ЗАО "IT-Технологии"'],
                "phone_number": "8-343-444-55-66",
            },
            {
                "organization_id": organizations['ЗАО "IT-Технологии"'],
                "phone_number": "8-343-555-66-77",
            },
            {
                "organization_id": organizations['ОАО "ВкусВилл"'],
                "phone_number": "8-843-666-77-88",
            },
            {
                "organization_id": organizations['ТОО "Уютный Дом"'],
                "phone_number": "8-495-777-88-99",
            },
            {
                "organization_id": organizations['ТОО "Уютный Дом"'],
                "phone_number": "8-495-888-99-00",
            },
            {
                "organization_id": organizations['ТОО "Уютный Дом"'],
                "phone_number": "8-800-123-45-67",
            },
        ],
    )


def downgrade() -> None:
    # Удаляем таблицы в правильном порядке
    op.drop_table("phone")
    op.drop_table("organization_activity")
    op.drop_table("organization")
    op.drop_table("activity")
    op.drop_table("building")
