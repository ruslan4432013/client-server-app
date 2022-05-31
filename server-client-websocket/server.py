import asyncio
import sys
import json

import websockets
import logging

from websockets.exceptions import ConnectionClosedError, ConnectionClosedOK
from websockets.legacy.client import WebSocketClientProtocol
from websockets.legacy.server import WebSocketServerProtocol

from log import server_log_config
from utils.message_processing import send_message
from config.settings import DEFAULT_PORT, MAX_CONNECTIONS, DEFAULT_IP_ADDRESS
from config.varibales_jim_protocol import ACTION, PRESENCE, ACCOUNT_NAME, USER, TIME, RESPONSE, ERROR, RESPONSE_200, \
    RESPONSE_400, MESSAGE, DESTINATION, SENDER, MESSAGE_TEXT, EXIT
from utils.decorators import log, Log
from utils.message_processing import parse_the_message

logger = logging.getLogger('server')


@log
async def process_client_message(message, messages_list, client, clients, names):
    """
    Обработчик сообщений от клиентов, принимает словарь - сообщение от клиента,
    проверяет корректность, отправляет словарь-ответ в случае необходимости.
    :param message:
    :param messages_list:
    :param client:
    :param clients:
    :param names:
    :return:
    """
    logger.debug(f'Разбор сообщения от клиента : {message}')
    # Если это сообщение о присутствии, принимаем и отвечаем
    try:
        if ACTION in message and message[ACTION] == PRESENCE and \
                TIME in message and USER in message:
            # Если такой пользователь ещё не зарегистрирован,
            # регистрируем, иначе отправляем ответ и завершаем соединение.
            if message[USER][ACCOUNT_NAME] not in names.keys():
                names[message[USER][ACCOUNT_NAME]] = client
                await send_message(client, RESPONSE_200)
            else:
                response = RESPONSE_400
                response[ERROR] = 'Имя пользователя уже занято.'
                await send_message(client, response)
                clients.remove(client)
                await client.close()
            return
        # Если это сообщение, то добавляем его в очередь сообщений.
        # Ответ не требуется.
        elif ACTION in message and message[ACTION] == MESSAGE and \
                DESTINATION in message and TIME in message \
                and SENDER in message and MESSAGE_TEXT in message:
            messages_list.append(message)
            return
        # Если клиент выходит
        elif ACTION in message and message[ACTION] == EXIT and ACCOUNT_NAME in message:
            clients.remove(names[message[ACCOUNT_NAME]])
            await names[message[ACCOUNT_NAME]].close()
            del names[message[ACCOUNT_NAME]]
            return
        # Иначе отдаём Bad request
        else:
            response = RESPONSE_400
            response[ERROR] = 'Запрос некорректен.'
            await send_message(client, response)
            return
    except ConnectionClosedOK:
        clients.remove(names[message[ACCOUNT_NAME]])
        del names[message[ACCOUNT_NAME]]


class Server:
    clients = []
    messages = []
    names = dict()

    async def register(self, ws: WebSocketServerProtocol):
        self.clients.append(ws)
        print('connected')
        logger.info(f'{ws.remote_address} connects')

    async def send_to_clients(self, message: str):
        if self.clients:
            await asyncio.gather(*(self.send_to_client(client, message) for client in self.clients))

    async def send_to_client(self, client: WebSocketClientProtocol, message):
        await process_client_message(message, self.messages, client, self.clients, self.names)
        await client.send(json.dumps(message))
        print('sending')

    async def ws_handler(self, ws: WebSocketServerProtocol, uri: str):
        await self.register(ws)
        try:
            await self.distribute(ws)

        # В случае, если клиент отключился
        except ConnectionClosedError:
            logger.info(f'Client {ws.remote_address} close connection')

    async def distribute(self, ws: WebSocketServerProtocol):
        async for message in ws:
            print(message)

            message_from_client = await parse_the_message(message)
            await self.send_to_clients(message_from_client)
            print(self.messages)


if __name__ == '__main__':
    server = Server()
    start_server = websockets.serve(server.ws_handler, DEFAULT_IP_ADDRESS, DEFAULT_PORT)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_server)
    loop.run_forever()
