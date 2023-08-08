import socket as s

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


def login_required(func):
    def checker(*args, **kwargs):
        from server.core import MessageProcessor
        from commons.variables import ACTION, PRESENCE
        if isinstance(args[0], MessageProcessor):
            found = False
            for arg in args:
                if isinstance(arg, s.socket):
                    for client in args[0].names:
                        if args[0].names[client] == arg:
                            found = True

            for arg in args:
                if isinstance(arg, dict):
                    if ACTION in arg and arg[ACTION] == PRESENCE:
                        found = True
            if not found:
                raise TypeError
        return func(*args, **kwargs)

    return checker

