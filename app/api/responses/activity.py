from pydantic import BaseModel


class ActivityResponse(BaseModel):
    """Схема для вида деятельности."""

    id: int
    name: str
    parent_id: int | None = None
