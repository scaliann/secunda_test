from sqlalchemy import Column, Integer, ForeignKey, String

from app.models.base import Base


class Organization(Base):
    """Модель для организаций."""

    __tablename__ = "organization"

    name = Column(String, nullable=False, unique=True)
    building_id = Column(Integer, ForeignKey("building.id"))
