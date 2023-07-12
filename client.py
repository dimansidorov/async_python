import json
import socket
import sys
import time
import argparse

from commons.utils import send_message, get_message, check_port, check_mode
from commons.variables import (
    ACCOUNT_NAME,
    ACTION,
    DEFAULT_PORT,
    DEFAULT_IP_ADDRESS,
    ERROR,
    MESSAGE,
    MESSAGE_TEXT,
    PRESENCE,
    SENDER,
    RESPONSE,
    TIME,
    USER
)

import logging
import logs.config_client_logs
from decorators import log

LOGGER = logging.getLogger('client')


@log
def get_message_from_server(message):
    if all([
        ACTION in message,
        message[ACTION] == MESSAGE,
        SENDER in message,
        MESSAGE_TEXT in message
    ]):
        LOGGER.info('Received a message from the user'
                    f'{message[SENDER]}:{message[MESSAGE_TEXT]}')
        print(f'{message[SENDER]}: {message[MESSAGE_TEXT]}')
    else:
        LOGGER.error(f'Received an invalid massage')


@log
def create_message(sock, account_name='Guest'):
    message = input('Enter a message to send or "exit" to terminate the program:  ')
    if message != 'exit':
        message_dict = {
            ACTION: MESSAGE,
            TIME: time.time(),
            ACCOUNT_NAME: account_name,
            MESSAGE_TEXT: message
        }
        LOGGER.info('A message has been generated')
        return message_dict

    sock.close()
    LOGGER.info('Termination of the service by the user')
    sys.exit(0)


@log
def create_presence_msg(account_name='Guest'):
    out = {
        ACTION: PRESENCE,
        TIME: time.time(),
        USER: {ACCOUNT_NAME: account_name}
    }
    return out


@log
def get_process_response_ans(message):
    LOGGER.info('getting answer from server')
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            return '200 : OK'
        return f'400 : {message[ERROR]}'
    raise ValueError


@log
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('addr', default=DEFAULT_IP_ADDRESS, nargs='?')
    parser.add_argument('port', default=DEFAULT_PORT, nargs='?')
    parser.add_argument('-m', '--mode', default='listen', nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    server_address = namespace.addr
    server_port = namespace.port
    client_mode = namespace.mode

    if not check_port(server_port):
        LOGGER.critical(
            f'Invalid port -  {server_port}.')
        sys.exit(1)

    if not check_mode(client_mode):
        LOGGER.critical(
            f'Invalid mode -  {client_mode}.')
        sys.exit(1)

    return server_address, server_port, client_mode


def main():
    server_address, server_port, client_mode = parse_args()

    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((server_address, server_port))
        send_message(client, create_presence_msg())
        answer = get_process_response_ans(get_message(client))
        LOGGER.info(f'{answer}')
    except json.JSONDecodeError:
        LOGGER.error(f'Error decoding json string')
    except ValueError:
        LOGGER.error('Error!')
    else:
        while True:
            try:
                if client_mode == 'listen':
                    a = get_message_from_server(get_message(client))
                else:
                    send_message(client, create_message(client))
            except Exception as err:
                LOGGER.error(f'The connection to the {server_address} server has been lost. Error: {err}')
                sys.exit(1)


if __name__ == '__main__':
    main()
