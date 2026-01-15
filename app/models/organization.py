from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship

from app.models.base import Base


class Organization(Base):
    __tablename__ = "organization"

    name = Column(String)
    building_id = Column(Integer, ForeignKey("building.id"))
