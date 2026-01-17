"""Add activity depth constraint

Revision ID: 1fe1a3983282
Revises: 4021fdd40029
Create Date: 2026-01-17 19:25:34.405129

"""

from typing import Sequence, Union

from alembic import op


revision: str = "1fe1a3983282"
down_revision: Union[str, Sequence[str], None] = "4021fdd40029"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    # 1. Создаем функцию для проверки глубины (отдельный execute)
    op.execute(
        """
        CREATE OR REPLACE FUNCTION check_activity_depth()
        RETURNS TRIGGER AS $$
        DECLARE
            current_depth INTEGER;
        BEGIN
            -- Если это корневая деятельность (нет родителя), разрешаем
            IF NEW.parent_id IS NULL THEN
                RETURN NEW;
            END IF;

            -- Получаем текущую глубину родителя
            WITH RECURSIVE activity_path AS (
                -- Начинаем с родителя
                SELECT id, parent_id, 1 AS depth
                FROM activity
                WHERE id = NEW.parent_id

                UNION ALL

                -- Поднимаемся вверх по родителям
                SELECT a.id, a.parent_id, ap.depth + 1
                FROM activity a
                INNER JOIN activity_path ap ON a.id = ap.parent_id
                WHERE ap.parent_id IS NOT NULL
            )
            SELECT MAX(depth) INTO current_depth
            FROM activity_path;

            -- Если родитель уже на глубине 3, запрещаем добавление
            IF current_depth >= 3 THEN
                RAISE EXCEPTION 'Activity depth cannot exceed 3 levels. Parent activity is already at level %', current_depth;
            END IF;

            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )

    # 2. Создаем триггер для проверки при вставке (отдельный execute)
    op.execute(
        """
        CREATE TRIGGER enforce_max_depth_on_insert
        BEFORE INSERT ON activity
        FOR EACH ROW
        EXECUTE FUNCTION check_activity_depth();
        """
    )

    # 3. Создаем триггер для проверки при обновлении (отдельный execute)
    op.execute(
        """
        CREATE TRIGGER enforce_max_depth_on_update
        BEFORE UPDATE ON activity
        FOR EACH ROW
        WHEN (NEW.parent_id IS DISTINCT FROM OLD.parent_id)
        EXECUTE FUNCTION check_activity_depth();
        """
    )


def downgrade() -> None:
    # Удаляем триггеры по отдельности
    op.execute("DROP TRIGGER IF EXISTS enforce_max_depth_on_update ON activity;")
    op.execute("DROP TRIGGER IF EXISTS enforce_max_depth_on_insert ON activity;")
