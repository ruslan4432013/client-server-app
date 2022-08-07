import argparse
import asyncio
import json
import sys

import time
from abc import ABC

import websockets
import logging

from websockets.exceptions import ConnectionClosedOK

from threading import Thread

from config.errors import IncorrectDataRecivedError, ReqFieldMissingError, ServerError
from log import client_log_config
from utils.decorators import log
from config.settings import DEFAULT_IP_ADDRESS, DEFAULT_PORT
from config.varibales_jim_protocol import ACTION, PRESENCE, TIME, USER, ACCOUNT_NAME, RESPONSE, ERROR, EXIT, MESSAGE, \
    SENDER, MESSAGE_TEXT, DESTINATION
from utils.message_processing import get_message, send_message, parse_the_message
from utils.metaclasses import ClientMaker

logger = logging.getLogger('client')


@log
async def process_response_ans(message):
    """
    Функция разбирает ответ сервера на сообщение о присутствии,
    возращает 200 если все ОК или генерирует исключение при ошибке
    :param message:
    :return:
    """
    logger.debug(f'Разбор приветственного сообщения от сервера: {message}')
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            return '200 : OK'
        elif message[RESPONSE] == 400:
            raise ServerError(f'400 : {message[ERROR]}')
    raise ReqFieldMissingError(RESPONSE)


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


@log
def arg_parser():
    """Парсер аргументов коммандной строки"""
    parser = argparse.ArgumentParser()
    parser.add_argument('addr', default=DEFAULT_IP_ADDRESS, nargs='?')
    parser.add_argument('port', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-n', '--name', default=None, nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    server_address = namespace.addr
    server_port = namespace.port
    client_name = namespace.name

    # проверим подходящий номер порта
    if not 1023 < server_port < 65536:
        logger.critical(
            f'Попытка запуска клиента с неподходящим номером порта: {server_port}. '
            f'Допустимы адреса с 1024 до 65535. Клиент завершается.')
        sys.exit(1)

    return server_address, server_port, client_name


class Executor(Thread):
    def __init__(self, args=(), target=None, **kwargs):
        super().__init__()
        self.target = target
        self.args = args

    def run(self):
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        new_loop.run_until_complete(self.target(*self.args))


class Client:
    def __init__(self, account_name, ws):
        self.account_name = account_name
        self.ws = ws


class ClientSender(Client, metaclass=ClientMaker):

    async def create_exit_message(self):
        """Функция создаёт словарь с сообщением о выходе"""
        return {
            ACTION: EXIT,
            TIME: time.time(),
            ACCOUNT_NAME: self.account_name
        }

    async def create_message(self):
        """
        Функция запрашивает кому отправить сообщение и само сообщение,
        и отправляет полученные данные на сервер
        """
        to_user = input('Введите получателя сообщения: ')
        message = input('Введите сообщение для отправки: ')
        message_dict = {
            ACTION: MESSAGE,
            SENDER: self.account_name,
            DESTINATION: to_user,
            TIME: time.time(),
            MESSAGE_TEXT: message
        }
        logger.debug(f'Сформирован словарь сообщения: {message_dict}')
        try:
            await send_message(self.ws, message_dict)
            logger.info(f'Отправлено сообщение для пользователя {to_user}')
        except Exception as e:
            print(e)
            logger.critical('Потеряно соединение с сервером.')
            sys.exit(1)

    async def user_interactive(self):
        """Функция взаимодействия с пользователем, запрашивает команды, отправляет сообщения"""
        await ClientSender.print_help()
        while True:

            command = input('Введите команду: ')
            if command == 'message':
                await self.create_message()
            elif command == 'help':
                await ClientSender.print_help()
            elif command == 'exit':
                await send_message(self.ws, await self.create_exit_message())
                print('Завершение соединения.')
                logger.info('Завершение работы по команде пользователя.')
                # Задержка неоходима, чтобы успело уйти сообщение о выходе
                await asyncio.sleep(0.5)
                break
            else:
                print('Команда не распознана, попробойте снова. help - вывести поддерживаемые команды.')

    @staticmethod
    async def print_help():
        """Функция выводящяя справку по использованию"""
        print('Поддерживаемые команды:')
        print('message - отправить сообщение. Кому и текст будет запрошены отдельно.')
        print('help - вывести подсказки по командам')
        print('exit - выход из программы')

    def run(self):
        user_interface = Executor(target=self.user_interactive, args=())
        user_interface.daemon = True
        user_interface.start()


class ClientReader(Client, metaclass=ClientMaker):

    async def message_from_server(self):
        """Функция - обработчик сообщений других пользователей, поступающих с сервера"""
        while True:
            try:
                message = await get_message(self.ws)
                if ACTION in message and message[ACTION] == MESSAGE and \
                        SENDER in message and DESTINATION in message \
                        and MESSAGE_TEXT in message and message[DESTINATION] == self.account_name:
                    print(f'\nПолучено сообщение от пользователя {message[SENDER]}:'
                          f'\n{message[MESSAGE_TEXT]}')
                    logger.info(f'Получено сообщение от пользователя {message[SENDER]}:'
                                f'\n{message[MESSAGE_TEXT]}')
                else:
                    logger.error(f'Получено некорректное сообщение с сервера: {message}')
            except IncorrectDataRecivedError:
                logger.error(f'Не удалось декодировать полученное сообщение.')
            except (OSError, ConnectionError, ConnectionAbortedError,
                    ConnectionResetError, json.JSONDecodeError, ConnectionClosedOK):
                logger.critical(f'Потеряно соединение с сервером.')
                break


async def main():
    """Сообщаем о запуске"""

    print('Консольный месседжер. Клиентский модуль.')

    # Загружаем параметы коммандной строки
    server_address, server_port, client_name = arg_parser()

    # Если имя пользователя не было задано, необходимо запросить пользователя.
    if not client_name:
        client_name = input('Введите имя пользователя: ')

    websocket_resource_url = f"ws://{server_address}:{server_port}"

    async with websockets.connect(websocket_resource_url) as ws:

        try:
            # Инициализация сокета и сообщение серверу о нашем появлении
            try:
                await send_message(ws, await create_presence(client_name))
                    
                answer = await process_response_ans(await get_message(ws))

                logger.info(f'Установлено соединение с сервером. Ответ сервера: {answer}')
                print(f'Установлено соединение с сервером.')
            except json.JSONDecodeError:
                logger.error('Не удалось декодировать полученную Json строку.')
                sys.exit(1)
            except ServerError as error:
                logger.error(f'При установке соединения сервер вернул ошибку: {error.text}')
                sys.exit(1)
            except ReqFieldMissingError as missing_error:
                logger.error(f'В ответе сервера отсутствует необходимое поле {missing_error.missing_field}')
                sys.exit(1)
            except (ConnectionRefusedError, ConnectionError):
                logger.critical(
                    f'Не удалось подключиться к серверу {server_address}:{server_port}, '
                    f'конечный компьютер отверг запрос на подключение.')
                sys.exit(1)
            except ConnectionClosedOK:
                print('Connection is closed')
                sys.exit(0)

            else:
                # Если соединение с сервером установлено корректно,
                # запускаем клиенский процесс приёма сообщний

                # затем запускаем отправку сообщений и взаимодействие с пользователем.
                ClientSender(client_name, ws).run()
                # затем запускаем отправку сообщений и взаимодействие с пользователем.

                # Watchdog основной цикл, если один из потоков завершён,
                # то значит или потеряно соединение или пользователь
                # ввёл exit. Поскольку все события обработываются в потоках,
                # достаточно просто завершить цикл.

                await ClientReader(client_name, ws).message_from_server()

        except (ValueError, json.JSONDecodeError):
            logger.error('Не удалось декодировать сообщение сервера.')


if __name__ == '__main__':
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
    except Exception as e:
        print(e)
