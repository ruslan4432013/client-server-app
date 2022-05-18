import os
import sys
from pathlib import Path
import logging
from logging.handlers import TimedRotatingFileHandler

from config.settings import LOGGING_LEVEL

# Настраиваем путь
PATH = Path(__file__).resolve().parent.parent
PATH = os.path.join(PATH, 'logs', 'server', 'server.log')

# Настраиваем формат сообщений
_formatter = logging.Formatter('%(asctime)s %(levelname)s %(module)s %(message)s ')

# Создаем обработчик
file_handler = TimedRotatingFileHandler(PATH, encoding='UTF-8', interval=1, when='D')
file_handler.setFormatter(_formatter)
file_handler.setLevel(logging.INFO)
stream_handler = logging.StreamHandler(sys.stderr)
stream_handler.setFormatter(_formatter)

# Создаем логгер и настраиваем его
logger = logging.getLogger('server')
logger.addHandler(file_handler)
logger.addHandler(stream_handler)
logger.setLevel(LOGGING_LEVEL)

# Отладка
if __name__ == '__main__':
    logger.critical('Критическая ошибка')
    logger.error('Ошибка')
    logger.debug('Отладочная информация')
    logger.info('Информационное сообщение')
