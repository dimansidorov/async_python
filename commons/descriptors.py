import logging
import sys

logger = logging.getLogger('server')


class Port:
    """
    The descriptor class for the port number.
    Allows you to use only ports 1023 to 65536.
    An exception is thrown when trying to set an unsuitable port number.
    """
    def __set_name__(self, owner, name):
        self.name = name

    def __set__(self, instance, value):
        if not 1023 < value < 65536:
            logger.critical(
                f'An attempt to start the server with an unsuitable port {value}.'
            )
            sys.exit(1)

        instance.__dict__[self.name] = value


