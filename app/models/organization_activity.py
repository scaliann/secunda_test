from sqlalchemy import Column, Integer, ForeignKey

from app.models.base import Base


class OrganizationActivity(Base):
    """Модель для деятельности организаций."""

    __tablename__ = "organization_activity"

    organization_id = Column(Integer, ForeignKey("organization.id"))
    activity_id = Column(Integer, ForeignKey("activity.id"))
