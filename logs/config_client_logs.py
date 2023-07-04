import sys
import os
import logging
from commons.variables import (
    ENCODING, LOGGING_FORMAT, LOGGING_LEVEL, LOGGER_CRITICAL, LOGGER_ERROR, LOGGER_INFO, LOGGER_DEBUG
)

CLIENT_FORMATTER = logging.Formatter(LOGGING_FORMAT)

PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'client.log')

STREAM_HANDLER = logging.StreamHandler(sys.stderr)
STREAM_HANDLER.setFormatter(CLIENT_FORMATTER)
STREAM_HANDLER.setLevel(logging.ERROR)
LOG_FILE = logging.FileHandler(PATH, encoding=ENCODING)
LOG_FILE.setFormatter(CLIENT_FORMATTER)

LOGGER = logging.getLogger('client')
LOGGER.addHandler(STREAM_HANDLER)
LOGGER.addHandler(LOG_FILE)
LOGGER.setLevel(LOGGING_LEVEL)

if __name__ == '__main__':
    LOGGER.critical(LOGGER_CRITICAL)
    LOGGER.error(LOGGER_ERROR)
    LOGGER.debug(LOGGER_DEBUG)
    LOGGER.info(LOGGER_INFO)
