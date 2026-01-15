from pydantic import BaseModel, computed_field


class OrganizationFilterSchema(BaseModel):
    """Схема для фильтров организаций."""

    building_ids: str | None = None
    activity_ids: str | None = None
    search_str: str | None = None

    @computed_field
    @property
    def building_ids_list(
        self,
    ) -> list[int]:
        return [
            int(building_id)
            for building_id in self.building_ids.split(",")
            if building_id.isdigit()
        ]

    @computed_field
    @property
    def activity_ids_list(
        self,
    ) -> list[int]:
        return [
            int(activity_id)
            for activity_id in self.activity_ids.split(",")
            if activity_id.isdigit()
        ]
