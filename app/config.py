import pathlib
from functools import lru_cache

from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from pathlib import Path


load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")


class Settings(BaseSettings):
    """Настройки проекта"""

    db_name: str = ""
    db_username: str = ""
    db_password: str = ""
    db_host: str = ""
    db_port: int
    db_echo: bool = False

    api_key: str = ""

    class Config:
        env_file = "../.env"


@lru_cache
def get_settings(env_file_path: str | None = None) -> Settings:
    """Get settings."""

    if not env_file_path:
        execution_directory = pathlib.Path(__file__).parent.parent.resolve()
        env_file_path = str(execution_directory / ".env")
    return Settings(_env_file=env_file_path, _env_file_encoding="utf-8")
