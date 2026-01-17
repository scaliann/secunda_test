from pydantic import BaseModel, computed_field


class OrganizationFilterSchema(BaseModel):
    """Схема для фильтров организаций."""

    organization_ids: str | None = None
    building_ids: str | None = None
    activity_ids: str | None = None
    search_str: str | None = None
    activity_search_str: str | None = None

    latitude: float | None = None
    longitude: float | None = None
    radius: float | None = None

    @computed_field
    @property
    def organization_ids_list(
        self,
    ) -> list[int]:
        return (
            [
                int(organization_id)
                for organization_id in self.organization_ids.split(",")
                if organization_id.isdigit()
            ]
            if self.organization_ids
            else None
        )

    @computed_field
    @property
    def building_ids_list(
        self,
    ) -> list[int]:
        return (
            [
                int(building_id)
                for building_id in self.building_ids.split(",")
                if building_id.isdigit()
            ]
            if self.building_ids
            else None
        )

    @computed_field
    @property
    def activity_ids_list(
        self,
    ) -> list[int]:
        return (
            [
                int(activity_id)
                for activity_id in self.activity_ids.split(",")
                if activity_id.isdigit()
            ]
            if self.activity_ids
            else None
        )
