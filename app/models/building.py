from sqlalchemy import Column, Integer, ForeignKey, String, Float

from app.models.base import Base


class Building(Base):
    __tablename__ = "building"

    id = Column(Integer, primary_key=True)
    address = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
