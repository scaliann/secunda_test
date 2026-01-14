from sqlalchemy import Table, Column, Integer, ForeignKey

from app.models.base import Base


class OrganizationActivity(Base):
    __tablename__ = "organization_activity"

    organization_id = Column(Integer, ForeignKey("organization.id"))
    activity_id = Column(Integer, ForeignKey("activity.id"))
