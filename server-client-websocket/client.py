import asyncio
import json
import socket
import sys
import time

import websockets

from config.settings import DEFAULT_IP_ADDRESS, DEFAULT_PORT
from config.varibales_jim_protocol import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, RESPONSE, ERROR
from utils.message_processing import get_message, send_message


async def create_presence(account_name='Guest'):
    out = {
        ACTION: PRESENCE,
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: account_name,
        }
    }
    return out


async def process_ans(message):
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            return '200 : OK'
        return f'400 : {message[ERROR]}'
    raise ValueError


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
        print('В качестве порта может быть указано только число в диапазоне от 1024 до 65535.')
        sys.exit(1)

    websocket_resource_url = f"ws://{server_address}:{server_port}"
    message_to_server = await create_presence()
    async with websockets.connect(websocket_resource_url) as ws:
        await send_message(ws, message_to_server)
        try:
            message = await get_message(ws)
            answer = await process_ans(message)
            print(answer)
        except (ValueError, json.JSONDecodeError):
            print('Не удалось декодировать сообщение сервера.')


if __name__ == '__main__':
    asyncio.run(main())
