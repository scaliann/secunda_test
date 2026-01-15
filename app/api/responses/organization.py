from pydantic import BaseModel, ConfigDict

from app.api.responses.activity import ActivityResponse
from app.api.responses.building import BuildingResponse


class OrganizationResponse(BaseModel):
    """Схема одной организации."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    building: BuildingResponse
    phones: list[str] | None = None
    activities: list[ActivityResponse] | None = None


class OrganizationsListResponse(BaseModel):
    """Схема для списка организаций."""

    model_config = ConfigDict(from_attributes=True)

    results: list[OrganizationResponse]
