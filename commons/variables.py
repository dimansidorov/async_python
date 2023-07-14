import logging

"""Settings"""
"""Default settings"""
DEFAULT_PORT = 7777
DEFAULT_IP_ADDRESS = '127.0.0.1'
MAX_CONNECTIONS = 5
MAX_PACKAGE_LENGTH = 1024
ENCODING = 'utf-8'

"""JIM keys"""
ACTION = 'action'
TIME = 'time'
USER = 'user'
ACCOUNT_NAME = 'account_name'
SENDER = 'from'
DESTINATION = 'to'

"""Additional keys"""
PRESENCE = 'presence'
RESPONSE = 'response'
ERROR = 'error'
MESSAGE = 'message'
MESSAGE_TEXT = 'message_text'
EXIT = 'exit'


"""Logging"""
LOGGING_LEVEL = logging.DEBUG
LOGGING_FORMAT = '%(asctime)s %(levelname)s %(filename)s %(message)s'
LOGGER_CRITICAL = 'CRITICAL ERROR'
LOGGER_ERROR = 'ERROR'
LOGGER_DEBUG = 'DEBUG INFO'
LOGGER_INFO = 'INFO'

"""Responces"""
RESPONSE_200 = {
    RESPONSE: 200
}
RESPONSE_400 = {
    RESPONSE: 400,
    ERROR: ''
}