import asyncio

import websockets
import logging

from websockets.exceptions import ConnectionClosedError, ConnectionClosedOK

from websockets.legacy.server import WebSocketServerProtocol

from client import Executor
from database.server_db_utils import ServerStorage
from utils.descriptors import Port
from utils.message_processing import send_message
from config.settings import DEFAULT_PORT, DEFAULT_IP_ADDRESS
from config.varibales_jim_protocol import (ACTION, PRESENCE, ACCOUNT_NAME, USER, TIME, ERROR, RESPONSE_200,
                                           RESPONSE_400, MESSAGE, DESTINATION, SENDER, MESSAGE_TEXT, EXIT)
from utils.message_processing import parse_the_message
from utils.metaclasses import ServerMaker

# SQLAlchemy imports
from database.server_database import async_session
from sqlalchemy.future import select

logger = logging.getLogger('server')


class Server(metaclass=ServerMaker):
    port = Port()
    database = ServerStorage(session=async_session)

    def __init__(self, listen_address=DEFAULT_IP_ADDRESS, listen_port=DEFAULT_PORT):
        self.addr = listen_address
        self.port = listen_port
        self.clients = []
        self.messages = []
        self.names = dict()
        self.loop = asyncio.get_event_loop()
        user_interface = Executor(target=self.get_info_from_db_by_command, args=())
        user_interface.daemon = True
        user_interface.start()

    def start(self):
        start_server = websockets.serve(self.ws_handler, self.addr, self.port)
        self.loop.run_until_complete(self.database.init_db())
        self.loop.run_until_complete(start_server)
        self.loop.run_forever()

    # Специальный метод, для удаления всех активных пользователей из бд
    async def stop(self):
        for login in self.names.keys():
            await self.database.user_logout(login)

    async def register(self, ws: WebSocketServerProtocol):
        self.clients.append(ws)
        logger.info(f'{ws.remote_address} connects')

    async def ws_handler(self, ws: WebSocketServerProtocol, _uri: str):
        await self.register(ws)
        try:
            await self.distribute(ws)

        # В случае, если клиент отключился
        except ConnectionClosedError:
            logger.info(f'Client {ws.remote_address} close connection')

            login = list(self.names.keys())[list(self.names.values()).index(ws)]

            del self.names[login]
            await self.database.user_logout(login)

    async def distribute(self, ws: WebSocketServerProtocol):
        async for message in ws:

            message_from_client = await parse_the_message(message)
            await self.process_client_message(message_from_client, self.messages, ws, self.clients, self.names)

            if self.messages:
                for i in self.messages:
                    try:
                        await self.process_message(i, self.names, self.clients)
                    except Exception:
                        logger.info(f'Связь с клиентом с именем {i[DESTINATION]} была потеряна')
                        self.clients.remove(self.names[i[DESTINATION]])
                        del self.names[i[DESTINATION]]
                self.messages.clear()

    @staticmethod
    async def process_message(message, names, listen_socks):
        """
        Функция адресной отправки сообщения определённому клиенту. Принимает словарь сообщение,
        список зарегистрированых пользователей и слушающие сокеты. Ничего не возвращает.
        :param message:
        :param names:
        :param listen_socks:
        :return:
        """
        if message[DESTINATION] in names and names[message[DESTINATION]] in listen_socks:
            await send_message(names[message[DESTINATION]], message)
            logger.info(f'Отправлено сообщение пользователю {message[DESTINATION]} '
                        f'от пользователя {message[SENDER]}.')
        elif message[DESTINATION] in names and names[message[DESTINATION]] not in listen_socks:
            raise ConnectionError
        else:
            logger.error(
                f'Пользователь {message[DESTINATION]} не зарегистрирован на сервере, '
                f'отправка сообщения невозможна.')

    async def process_client_message(self, message, messages_list, client, clients, names):
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

                    # Получаем логин, ip и порт подключаемого клиента
                    login = message[USER][ACCOUNT_NAME]
                    ip_address, port = client.remote_address
                    # Регистрируем пользователя в базе данных
                    await self.database.register_client(login, ip_address, port)

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

                # Удаляем пользователя из базы активных
                login = message[ACCOUNT_NAME]
                await self.database.user_logout(login)

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
            login = message[ACCOUNT_NAME]
            await self.database.user_logout(login)
            del names[message[ACCOUNT_NAME]]

    async def get_info_from_db_by_command(self):
        while True:
            command = input('Введите команду: ')
            if command == 'help':
                print_help()
            elif command == 'exit':
                break
            elif command == 'users':
                for user in sorted(await self.database.users_list()):
                    print(f'Пользователь {user[0]}, последний вход: {user[1]}')
            elif command == 'connected':
                for user in sorted(await self.database.active_users_list()):
                    print(
                        f'Пользователь {user[0]}, подключен: {user[1]}:{user[2]}, время установки соединения: {user[3]}')
            elif command == 'loghist':
                name = input('Введите имя пользователя для просмотра истории. '
                             'Для вывода всей истории, просто нажмите Enter: ')
                for user in sorted(await self.database.login_history(name)):
                    print(f'Пользователь: {user[0]} время входа: {user[1]}. Вход с: {user[2]}:{user[3]}')


def print_help():
    print('Поддерживаемые комманды:')
    print('users - список известных пользователей')
    print('connected - список подключённых пользователей')
    print('loghist - история входов пользователя')
    print('exit - завершение работы сервера.')
    print('help - вывод справки по поддерживаемым командам')


if __name__ == '__main__':

    server = Server()
    try:
        print_help()
        server.start()
    except Exception as e:
        print(e)
    finally:
        asyncio.run(server.stop())
        input()
