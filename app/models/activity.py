from sqlalchemy import Column, Integer, ForeignKey, String

from app.models.base import Base


class Activity(Base):
    """Модель для деятельности."""

    __tablename__ = "activity"

    name = Column(String, nullable=False, unique=True)
    parent_id = Column(Integer, ForeignKey("activity.id"))
