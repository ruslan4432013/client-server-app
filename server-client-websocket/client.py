import argparse
import asyncio
import json
import sys
import time
from asyncio import start_server
from concurrent.futures import ThreadPoolExecutor

import websockets
import logging

from websockets.legacy.client import WebSocketClientProtocol
from websockets.legacy.server import WebSocketServerProtocol

from log import client_log_config
from utils.decorators import log
from config.settings import DEFAULT_IP_ADDRESS, DEFAULT_PORT
from config.varibales_jim_protocol import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, RESPONSE, ERROR, MESSAGE, SENDER, \
    MESSAGE_TEXT
from utils.message_processing import get_message, send_message, create_message

logger = logging.getLogger('client')


@log
async def create_presence(account_name='Guest'):
    out = {
        ACTION: PRESENCE,
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: account_name,
        }
    }
    return out


@log
async def process_ans(message):
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            return '200 : OK'
        return f'400 : {message[ERROR]}'
    raise ValueError


async def ainput(prompt: str = "") -> str:
    with ThreadPoolExecutor(1, "AsyncInput") as executor:
        return await asyncio.get_event_loop().run_in_executor(executor, input, prompt)


async def main():
    try:
        server_address = sys.argv[1]
        server_port = int(sys.argv[2])
        if server_port < 1024 or server_port > 65535:
            raise ValueError
    except IndexError:
        server_address = DEFAULT_IP_ADDRESS
        server_port = DEFAULT_PORT
    except ValueError:
        logger.error('В качестве порта может быть указано только число в диапазоне от 1024 до 65535.')
        sys.exit(1)

    websocket_resource_url = f"ws://{server_address}:{server_port}"
    message_to_server = await create_presence()
    async with websockets.connect(websocket_resource_url) as ws:
        try:
            while True:
                message = await ainput("Enter your message: ")
                await ws.send(message)
                print(await ws.recv())

        except (ValueError, json.JSONDecodeError):
            logger.error('Не удалось декодировать сообщение сервера.')





if __name__ == '__main__':
    asyncio.run(main())
