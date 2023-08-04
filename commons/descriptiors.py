from sqlalchemy import values

import logging

logger = logging.getLogger('server')


class Port:
    def __set_name__(self, owner, name):
        self.name = name

    def __set__(self, instance, value):
        if not 1023 < value < 65536:
            logger.critical(
                f'An attempt to start the server with an unsuitable port {value}.'
            )
            exit(1)

        instance.__dict__[self.name] = value


