import logging
import typing as t

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

log = logging.getLogger(__name__)


class DatabaseSettings(BaseSettings):
    host: str
    port: int
    db: str
    user: str
    password: str
    min_pool_size: int
    max_pool_size: int
    command_timeout: t.Optional[float] = Field(default=None)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="POSTGRES_",
        case_sensitive=False,
        extra="ignore",
    )


class ApplicationSettings(BaseSettings):
    version: str
    name: str
    port: int
    host: str
    reload: bool
    log_level: str
    base_api_url: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="APP_",
        case_sensitive=False,
        extra="ignore",
    )


class Settings(BaseSettings):
    app: ApplicationSettings = Field(default_factory=lambda: ApplicationSettings()) # type: ignore
    database: DatabaseSettings = Field(default_factory=lambda: DatabaseSettings()) # type: ignore

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


LOG_FORMAT_DEBUG = "%(levelname)s:%(message)s:%(pathname)s:%(funcName)s:%(lineno)d"


def configure_logging(level: str | None = None) -> None:
    lvl = level if level else settings.app.log_level

    numeric = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARN": logging.WARN,
        "WARNING": logging.WARN,
        "ERROR": logging.ERROR,
    }.get(lvl.upper(), logging.ERROR)
    fmt = LOG_FORMAT_DEBUG if numeric == logging.DEBUG else "%(levelname)s:%(message)s"
    logging.basicConfig(level=numeric, format=fmt)


settings = Settings()

__all__ = ["settings", "configure_logging"]
