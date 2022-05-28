import sys
import logging

from logs import server_log_config, client_log_config

if sys.argv[0].find('client') == -1:
    LOGGER = logging.getLogger('server')
else:
    LOGGER = logging.getLogger('client')


def log(func_to_log):
    def log_saver(*args, **kwargs):
        res = func_to_log(*args, **kwargs)
        LOGGER.debug(f'The function {func_to_log.__name__} has been called with parameters {args}, {kwargs}. '
                     f'Call from a module {func_to_log.__module__}', stacklevel=2)
        return res

    return log_saver
