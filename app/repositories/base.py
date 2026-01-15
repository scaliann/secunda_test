from typing import Generic, TypeVar

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session

TypeModel = TypeVar("TypeModel")


class Repository(Generic[TypeModel]):
    """Базовый репозиторий."""

    model: type[TypeModel] = None

    def __init__(self, session: AsyncSession = Depends(get_session)):
        self.session = session
