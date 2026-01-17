from sqlalchemy import Column, Integer, ForeignKey, String

from app.models.base import Base


class Phone(Base):
    """Модель для телефонов."""

    __tablename__ = "phone"

    id = Column(Integer, primary_key=True)
    organization_id = Column(Integer, ForeignKey("organization.id"))
    phone_number = Column(String, nullable=False)
