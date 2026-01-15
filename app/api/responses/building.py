from pydantic import BaseModel


class BuildingResponse(BaseModel):
    """Схема для здания."""

    id: int
    address: str
    latitude: float | None = None
    longitude: float | None = None
