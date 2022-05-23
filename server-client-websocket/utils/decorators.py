import inspect
from functools import wraps
from log import client_log_config, server_log_config
import logging
import sys

if sys.argv[0].find('client') == -1:
    LOGGER = logging.getLogger('server')
else:
    LOGGER = logging.getLogger('client')


def log(func):
    @wraps(func)
    def log_saver(*args, **kwargs):
        res = func(*args, **kwargs)
        LOGGER.info(f'Была вызвана функция {func.__name__} c параметрами {args}, {kwargs}.'
                    f'Вызов из модуля {func.__module__}.'
                    f'Вызов из функции {inspect.stack()[1][3]}.', stacklevel=2)

        return res

    return log_saver


class Log:

    def __call__(self, func):
        @wraps(func)
        def log_saver(*args, **kwargs):
            res = func(*args, **kwargs)
            LOGGER.info(f'Была вызвана функция {func.__name__} c параметрами {args}, {kwargs}.'
                        f'Вызов из модуля {func.__module__}.'
                        f'Вызов из функции {inspect.stack()[1][3]}.', stacklevel=2)
            return res

        return log_saver
