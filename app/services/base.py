from typing import TypeVar
from functools import cached_property

T = TypeVar("T")


def get_repository[T](repo_cls: type[T]) -> T:
    """Получить репозиторий."""

    def _get_repository(self) -> T:
        return repo_cls(self.session)

    return cached_property(_get_repository)
