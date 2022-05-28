import os
import sys
from pathlib import Path
import logging
from logging.handlers import TimedRotatingFileHandler

from config.settings import LOGGING_LEVEL

# Настраиваем путь
PATH = Path(__file__).resolve().parent.parent
PATH = os.path.join(PATH, 'logs', 'client', 'client.log')

# Настраиваем формат сообщений
_formatter = logging.Formatter('%(asctime)s %(levelname)s %(module)s %(message)s ')

# Создаем обработчик
file_handler = logging.FileHandler(PATH, encoding='UTF-8')
file_handler.setFormatter(_formatter)
file_handler.setLevel(logging.INFO)


# Создаем логгер и настраиваем его
logger = logging.getLogger('client')
logger.addHandler(file_handler)
logger.setLevel(LOGGING_LEVEL)

# Отладка
if __name__ == '__main__':
    logger.critical('Критическая ошибка')
    logger.error('Ошибка')
    logger.debug('Отладочная информация')
    logger.info('Информационное сообщение')
