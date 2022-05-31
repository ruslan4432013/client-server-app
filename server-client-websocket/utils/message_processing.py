import json
import sys
import time

from websockets.legacy.client import WebSocketClientProtocol

from config.errors import IncorrectDataRecivedError
from config.settings import ENCODING
from config.varibales_jim_protocol import ACTION, MESSAGE, TIME, ACCOUNT_NAME, MESSAGE_TEXT
from utils.decorators import log


@log
async def parse_the_message(message):
    if isinstance(message, bytes):
        json_response = message.decode(ENCODING)
        response = json.loads(json_response)
        if isinstance(response, dict):
            return response
        else:
            raise IncorrectDataRecivedError
    else:
        raise IncorrectDataRecivedError


@log
async def get_message(client: WebSocketClientProtocol):
    encoded_response = await client.recv()
    return await parse_the_message(encoded_response)


@log
async def send_message(websocket: WebSocketClientProtocol, message):
    js_message = json.dumps(message)
    encoded_message = js_message.encode(ENCODING)
    await websocket.send(encoded_message)


@log
async def create_message(websocket: WebSocketClientProtocol, account_name='Guest'):
    message = input('Введите сообщение для отправки или \'!!!\' для завершения работы: ')
    if message == '!!!':
        await websocket.close()

        print('Спасибо за использование нашего сервиса!')
        sys.exit(0)
    message_dict = {
        ACTION: MESSAGE,
        TIME: time.time(),
        ACCOUNT_NAME: account_name,
        MESSAGE_TEXT: message
    }

    return message_dict
