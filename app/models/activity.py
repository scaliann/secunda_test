from sqlalchemy import Column, Integer, ForeignKey, String

from app.models.base import Base


class Activity(Base):
    __tablename__ = "activity"

    name = Column(String)
    parent_id = Column(Integer, ForeignKey("activity.id"))
