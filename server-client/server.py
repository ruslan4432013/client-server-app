import socket
import sys
import argparse
import logging
import select
import time
from config.settings import DEFAULT_PORT, MAX_CONNECTIONS
from config.varibales_jim_protocol import ACTION, TIME, USER, ACCOUNT_NAME, SENDER, PRESENCE, RESPONSE, ERROR, MESSAGE, \
    MESSAGE_TEXT
from utils.message_processing import get_message, send_message
from utils.decos import log

logger = logging.getLogger('server')


@log
def process_client_message(message, messages_list, client):
    logger.debug(f'Parsing a message from a client: {message}')

    correct_action = ACTION in message and message[ACTION] == PRESENCE

    if correct_action and TIME in message and USER in message and message[USER][ACCOUNT_NAME] == 'Guest':
        send_message(client, {RESPONSE: 200})
        return

    elif ACTION in message and message[ACTION] == MESSAGE and \
            TIME in message and MESSAGE_TEXT in message:
        messages_list.append((message[ACCOUNT_NAME], message[MESSAGE_TEXT]))
        return

    else:
        send_message(client, {
            RESPONSE: 400,
            ERROR: 'Bad Request'
        })
        return


@log
def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-a', default='', nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    listen_address = namespace.a
    listen_port = namespace.p

    if not 1023 < listen_port < 65536:
        logger.critical(
            f'Attempt to start the server with the wrong port '
            f'{listen_port}. Valid addresses are 1024 to 65535.')
        sys.exit(1)

    return listen_address, listen_port


def main():
    listen_address, listen_port = arg_parser()

    logger.info(
        f'Server started, connection port: {listen_port}, '
        f'address from which connections are accepted:{listen_address}. '
        f'If no address is specified, connections from any address are accepted.')

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((listen_address, listen_port))
    sock.settimeout(0.5)

    clients = set()
    messages = []

    sock.listen(MAX_CONNECTIONS)

    while True:
        try:
            client, client_address = sock.accept()
        except OSError:
            pass
        else:
            logger.info(f'PC connection established {client_address}')
            clients.add(client)

        recv_data_lst = []
        send_data_lst = []
        err_lst = []

        try:
            if clients:
                recv_data_lst, send_data_lst, err_lst = select.select(clients, clients, [], 0)
        except OSError:
            pass

        if recv_data_lst:
            for client_with_message in recv_data_lst:
                try:
                    process_client_message(get_message(client_with_message),
                                           messages, client_with_message)
                except Exception as e:
                    logger.info(f'client {client_with_message.getpeername()} '
                                f'disconnected from the server.')
                    clients.remove(client_with_message)

        if messages and send_data_lst:
            message = {
                ACTION: MESSAGE,
                SENDER: messages[0][0],
                TIME: time.time(),
                MESSAGE_TEXT: messages[0][1]
            }
            del messages[0]
            for waiting_client in send_data_lst:
                try:
                    send_message(waiting_client, message)
                except Exception as e:
                    logger.info(f'Client {waiting_client.getpeername()} disconnected from the server.')
                    clients.remove(waiting_client)


if __name__ == '__main__':
    try:
        main()
        print('server is running')
    except Exception as e:
        print(e)
        input('Press any key to exit')
