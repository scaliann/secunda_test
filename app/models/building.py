from sqlalchemy import Column, Integer, String, Float

from app.models.base import Base


class Building(Base):
    """Модель для зданий."""

    __tablename__ = "building"

    id = Column(Integer, primary_key=True)
    address = Column(String, unique=True, nullable=False)
    latitude = Column(Float, unique=True, nullable=False)
    longitude = Column(Float, unique=True, nullable=False)
