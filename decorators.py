import logs.config_client_logs
import logs.config_server_logs
import logging
import sys
import inspect
import traceback


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
                     f'Call from function {traceback.format_stack()[0].strip().split()[-1]}', stacklevel=2)
        return result

    return wrapper

