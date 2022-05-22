import asyncio
import sys
import json

import websockets
import logging
from log import server_log_config
from client import send_message
from config.settings import DEFAULT_PORT, MAX_CONNECTIONS
from config.varibales_jim_protocol import ACTION, PRESENCE, ACCOUNT_NAME, USER, TIME, RESPONSE, ERROR
from utils.decorators import log, Log
from utils.message_processing import get_message

logger = logging.getLogger('server')


@Log()
def process_client_message(message):
    correct_action = message[ACTION] == PRESENCE if ACTION in message else False

    correct_account_name = message[USER][ACCOUNT_NAME] == 'Guest' if USER in message else False

    correct_message = all((TIME in message,
                           USER in message,
                           ACTION in message,
                           correct_action,
                           correct_account_name))

    if correct_message:
        logger.info('get correct message')
        return {RESPONSE: 200}

    logger.warning(f'get incorrect message: {message}')
    return {
        RESPONSE: 400,
        ERROR: 'Bad Request'
    }


@Log()
def bind():
    try:
        if '-p' in sys.argv:
            listen_port = int(sys.argv[sys.argv.index('-p') + 1])
        else:
            listen_port = DEFAULT_PORT
        if listen_port < 1024 or listen_port > 65535:
            raise ValueError
    except IndexError:
        logger.error('После параметра -\'p\' необходимо указать номер порта.')
        sys.exit(1)
    except ValueError:
        logger.error('В качестве порта может быть указано только число в диапазоне от 1024 до 65535.')
        sys.exit(1)

    try:
        if '-a' in sys.argv:
            listen_address = sys.argv[sys.argv.index('-a') + 1]
        else:
            listen_address = 'localhost'

    except IndexError:
        logger.error('После параметра \'a\'- необходимо указать адрес, который будет слушать сервер.')
        sys.exit(1)

    logger.info(f'ws://{listen_address}:{listen_port} was created')
    return listen_address, listen_port


async def handler(websocket, path):
    try:
        message_from_client = await get_message(websocket)
        logger.info(f'get message message: {message_from_client}')

        response = process_client_message(message_from_client)
        await send_message(websocket, response)

    except (ValueError, json.JSONDecodeError):
        logger.error('Принято некорректное сообщение от клиента.')


async def main():
    listen_address, listen_port = bind()
    async with websockets.serve(handler, listen_address, listen_port):
        await asyncio.Future()


if __name__ == '__main__':
    asyncio.run(main())
