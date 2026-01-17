from collections.abc import AsyncGenerator
from os import environ
from uuid import uuid4

from asyncpg import Connection
from sqlalchemy import NullPool
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import get_settings

settings = get_settings()


def get_database_url(for_alembic: bool = False) -> URL:
    """Get database url."""
    port = settings.db_port
    if for_alembic:
        port = int(environ.get("MIGRATE_DB_PORT", "0")) or settings.db_port
    return URL.create(
        drivername="postgresql+asyncpg",
        username=settings.db_username,
        password=settings.db_password,
        host=settings.db_host,
        port=port,
        database=settings.db_name,
    )


class CustomConnection(Connection):
    """CustomConnection class."""

    def _get_unique_id(self, prefix: str) -> str:
        return f"__asyncpg_{prefix}_{uuid4()}__"


url = URL.create(
    drivername="postgresql+asyncpg",
    username=settings.db_username,
    password=settings.db_password,
    host=settings.db_host,
    port=settings.db_port,
    database=settings.db_name,
)

async_engine = create_async_engine(
    url,
    poolclass=NullPool,
    connect_args={
        "statement_cache_size": 0,
        "prepared_statement_cache_size": 0,
        "connection_class": CustomConnection,
    },
    echo=settings.db_echo,
)

async_session = async_sessionmaker(async_engine, expire_on_commit=False)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Получить сессию."""

    async with (
        async_engine.begin() as connection,
        async_session(bind=connection) as session,
    ):
        yield session
