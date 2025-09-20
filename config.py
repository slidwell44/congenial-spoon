import logging

from pydantic import BaseModel
from starlette.config import Config

from enums import PeopleManagementEnum

log = logging.getLogger(__name__)


class BaseConfigurationModel(BaseModel):
    pass


config = Config(".env")

LOG_LEVEL = config("LOG_LEVEL", default=logging.WARNING)

LOG_FORMAT_DEBUG = "%(levelname)s:%(message)s:%(pathname)s:%(funcName)s:%(lineno)d"

class LogLevels(PeopleManagementEnum):
    info = "INFO"
    warn = "WARN"
    error = "ERROR"
    debug = "DEBUG"


def configure_logging():
    log_level = str(LOG_LEVEL).upper()
    log_levels = list(LogLevels)

    if log_level not in log_levels:
        logging.basicConfig(level=LogLevels.error)
        return

    if log_level == LogLevels.debug:
        logging.basicConfig(level=log_level, format=LOG_FORMAT_DEBUG)
        return

    logging.basicConfig(level=log_level)

