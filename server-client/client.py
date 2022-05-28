import sys
import json
import socket
import time
import argparse
import logging
from config.settings import DEFAULT_PORT, DEFAULT_IP_ADDRESS
from config.varibales_jim_protocol import ACTION, TIME, USER, ACCOUNT_NAME, SENDER, PRESENCE, RESPONSE, ERROR, MESSAGE, \
    MESSAGE_TEXT
from utils.message_processing import get_message, send_message
from config.errors import ReqFieldMissingError, ServerError
from utils.decos import log


logger = logging.getLogger('client')


@log
def message_from_server(message):
    if ACTION in message and message[ACTION] == MESSAGE and \
            SENDER in message and MESSAGE_TEXT in message:
        print(f'Message received from user {message[SENDER]}:\n{message[MESSAGE_TEXT]}')
        logger.info(f'Message received from user {message[SENDER]}:\n{message[MESSAGE_TEXT]}')
    else:
        logger.error(f'An invalid message was received from the server: {message}')


@log
def create_message(sock, account_name='Guest'):
    message = input('Enter a message to send or \'exit\' to exit:')
    if message == 'exit':
        sock.close()
        logger.info('Shutdown by user command.')
        print('Thank you for using our service!')
        sys.exit(0)
    message_dict = {
        ACTION: MESSAGE,
        TIME: time.time(),
        ACCOUNT_NAME: account_name,
        MESSAGE_TEXT: message
    }
    logger.debug(f'The message dictionary is generated: {message_dict}')
    return message_dict


@log
def create_presence(account_name='Guest'):
    out = {
        ACTION: PRESENCE,
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: account_name
        }
    }
    logger.debug(f'Formed {PRESENCE} message to user {account_name}')
    return out


@log
def process_response_ans(message):
    logger.debug(f'Parsing the welcome message from the server: {message}')
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            return '200 : OK'
        elif message[RESPONSE] == 400:
            raise ServerError(f'400 : {message[ERROR]}')
    raise ReqFieldMissingError(RESPONSE)


@log
def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('addr', default=DEFAULT_IP_ADDRESS, nargs='?')
    parser.add_argument('port', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-m', '--mode', default='listen', nargs='?')
    parser.add_argument('-u', default='Guest', nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    server_address = namespace.addr
    server_port = namespace.port
    client_mode = namespace.mode


    if not 1023 < server_port < 65536:
        logger.critical(
            f'Attempting to start a client with the wrong port number: {server_port}. '
            f'Valid addresses are 1024 to 65535. The client ends.')
        sys.exit(1)


    if client_mode not in ('listen', 'send'):
        logger.critical(f'Invalid operating mode specified {client_mode}, '
                        f'allowedModes: listen , send')
        sys.exit(1)

    return server_address, server_port, client_mode


def main():

    server_address, server_port, client_mode = arg_parser()

    logger.info(
        f'Started client with parameters: server address: {server_address}, '
        f'port: {server_port}, working mode: {client_mode}')


    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((server_address, server_port))
        send_message(sock, create_presence())
        answer = process_response_ans(get_message(sock))
        logger.info(f'A connection to the server has been established. Server response: {answer}')
        print(f'A connection to the server has been established.')
    except json.JSONDecodeError:
        logger.error('Failed to decode received Json string.')
        sys.exit(1)
    except ServerError as error:
        logger.error(f'When establishing a connection, the server returned an error: {error.text}')
        sys.exit(1)
    except ReqFieldMissingError as missing_error:
        logger.error(f'A required field is missing in the server response {missing_error.missing_field}')
        sys.exit(1)
    except ConnectionRefusedError:
        logger.critical(
            f'Failed to connect to server {server_address}:{server_port}, '
            f'the destination computer denied the connection request.')
        sys.exit(1)
    else:

        if client_mode == 'send':
            print('Operating mode - sending messages.')
        else:
            print('Operating mode - receiving messages.')
        while True:

            if client_mode == 'send':
                try:
                    send_message(sock, create_message(sock))
                except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
                    logger.error(f'Server connection {server_address} was lost.')
                    sys.exit(1)


            if client_mode == 'listen':
                try:
                    message_from_server(get_message(sock))
                except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
                    logger.error(f'Server connection {server_address} was lost.')
                    sys.exit(1)


if __name__ == '__main__':
    main()
