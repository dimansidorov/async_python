import logs.config_client_logs
import logs.config_server_logs
import logging
import sys
import inspect


if 'client' in sys.argv[0]:
    LOGGER = logging.getLogger('client')
else:
    LOGGER = logging.getLogger('server')


def log(func):
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        LOGGER.debug(f'Calling function {func.__name__}; '
                     f'Parameters: {args}, {", ".join([f"{k}={v}" for k, v in kwargs.items()])}; '
                     f'Module: {func.__module__}; '
                     f'Call from function {inspect.stack()[1][3]}')
        return result

    return wrapper

