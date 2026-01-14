from sqlalchemy import Column, Integer
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base model."""

    id = Column(Integer, primary_key=True, doc="Идентификатор")
