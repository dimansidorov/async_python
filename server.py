import time
import select
import socket
import sys
import argparse
from commons.variables import (
    ACCOUNT_NAME,
    ACTION,
    DEFAULT_PORT,
    DESTINATION,
    ERROR,
    EXIT,
    MAX_CONNECTIONS,
    MESSAGE,
    MESSAGE_TEXT,
    PRESENCE,
    RESPONSE_200,
    RESPONSE_400,
    SENDER,
    TIME,
    USER
)

from commons.utils import get_message, send_message, check_port
import logging
import logs.config_server_logs
from decorators import log
from descriptiors import Port
from metaclasses import ServerVerifier

LOGGER = logging.getLogger('server')


@log
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-a', default='', nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    listen_port = namespace.p
    listen_address = namespace.a

    if not check_port(listen_port):
        LOGGER.critical(f'Invalid port -  {listen_port}.')
        sys.exit(1)

    return listen_address, listen_port


class Server(metaclass=ServerVerifier):
    port = Port()

    def __init__(self, address, port):
        self.address = address
        self.port = port
        self.sock = None
        self.clients = []
        self.messages = []
        self.names = {}

    def process_client_message(self, message, client) -> None:
        if all([ACTION in message, message[ACTION] == PRESENCE, TIME in message, USER in message]):
            if message[USER][ACCOUNT_NAME] not in self.names.keys():
                self.names[message[USER][ACCOUNT_NAME]] = client
                send_message(client, RESPONSE_200)
            else:
                response = RESPONSE_400
                response[ERROR] = 'The username is already taken.'
                send_message(client, response)
                self.clients.remove(client)
                client.close()

        elif all([ACTION in message, message[ACTION] == MESSAGE,
                  DESTINATION in message, TIME in message,
                  SENDER in message, MESSAGE_TEXT in message]):
            self.messages.append(message)

        elif all([ACTION in message, message[ACTION] == EXIT, ACCOUNT_NAME in message]):
            self.clients.remove(self.names[message[ACCOUNT_NAME]])
            self.names[message[ACCOUNT_NAME]].close()
            del self.names[message[ACCOUNT_NAME]]

        else:
            response = RESPONSE_400
            response[ERROR] = 'The request is incorrect.'
            send_message(client, response)

    def process_message(self, message, listen_socks):
        if all([message[DESTINATION] in self.names, self.names[message[DESTINATION]] in listen_socks]):
            send_message(self.names[message[DESTINATION]], message)
            LOGGER.info(f'A message was sent to the user {message[DESTINATION]} from the user {message[SENDER]}.')

        elif all([message[DESTINATION] in self.names, self.names[message[DESTINATION]] not in listen_socks]):
            raise ConnectionError

        else:
            LOGGER.error(f'User {message[DESTINATION]} is not registered on the server')

    def init_socket(self):
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.bind((self.address, self.port))
        transport.settimeout(0.5)

        self.sock = transport
        self.sock.listen()

    def main_loop(self):
        self.init_socket()

        while True:
            try:
                client, client_address = self.sock.accept()
                LOGGER.info(f'Connection established with {client_address}')
            except OSError:
                pass
            else:
                self.clients.append(client)

            recv_data_lst, send_data_lst, err_lst = [], [], []

            try:
                if self.clients:
                    recv_data_lst, send_data_lst, err_lst = select.select(self.clients, self.clients, [], 0)
            except OSError:
                pass

                if recv_data_lst:
                    for client_with_message in recv_data_lst:
                        try:
                            self.process_client_message(get_message(client_with_message), client_with_message)
                        except Exception as err:
                            LOGGER.error(f'{str(err)}')
                            LOGGER.info(f'The client {client_with_message.getpeername()} disconnected from the server')
                            self.clients.remove(client_with_message)

                for message in self.messages:
                    try:
                        self.process_message(message, send_data_lst)
                    except Exception as err:
                        LOGGER.error(str(err))
                        LOGGER.info(f'The client {message[DESTINATION]}  disconnected from the server')
                        self.clients.remove(self.names[message[DESTINATION]])
                self.messages.clear()


def main() -> None:
    listen_address, listen_port = parse_args()

    server = Server(listen_address, listen_port)
    server.main_loop()


if __name__ == '__main__':
    main()
