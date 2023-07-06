import sys
import os
import logging.handlers
import logging
from commons.variables import (
    ENCODING, LOGGING_LEVEL, LOGGING_FORMAT, LOGGER_CRITICAL, LOGGER_INFO, LOGGER_DEBUG, LOGGER_ERROR
)

SERVER_FORMATTER = logging.Formatter(LOGGING_FORMAT)

PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'server_logs/server.log')

STREAM_HANDLER = logging.StreamHandler(sys.stderr)
STREAM_HANDLER.setFormatter(SERVER_FORMATTER)
STREAM_HANDLER.setLevel(logging.ERROR)
LOG_FILE = logging.handlers.TimedRotatingFileHandler(PATH, encoding=ENCODING, interval=1, when='s')
LOG_FILE.setFormatter(SERVER_FORMATTER)

LOGGER = logging.getLogger('server')
LOGGER.addHandler(STREAM_HANDLER)
LOGGER.addHandler(LOG_FILE)
LOGGER.setLevel(LOGGING_LEVEL)


if __name__ == '__main__':
    LOGGER.critical(LOGGER_CRITICAL)
    LOGGER.error(LOGGER_ERROR)
    LOGGER.debug(LOGGER_DEBUG)
    LOGGER.info(LOGGER_INFO)
