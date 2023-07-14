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

LOGGER = logging.getLogger('server')


@log
def process_client_message(message, messages_list, client, clients, names) -> None:
    LOGGER.debug(f'Parsing a message from a client : {message}')
    if all([ACTION in message, message[ACTION] == PRESENCE, TIME in message, USER in message]):
        if message[USER][ACCOUNT_NAME] not in names:
            names[message[USER][ACCOUNT_NAME]] = client
            response = RESPONSE_200
            send_message(client, response)
        else:
            response = RESPONSE_400
            response[ERROR] = 'The username is already taken.'
            send_message(client, response)
            clients.remove(client)
            client.close()

    elif all([ACTION in message, message[ACTION] == MESSAGE, TIME in message, MESSAGE_TEXT in message]):
        messages_list.append(message)

    elif all([ACTION in message, message[ACTION] == EXIT, ACCOUNT_NAME in message]):
        clients.remove(names[message[ACCOUNT_NAME]])
        names[message[ACCOUNT_NAME]].close()
        del names[message[ACCOUNT_NAME]]

    else:
        response = RESPONSE_400
        response[ERROR] = 'Bad Request'
        send_message(client, response)


@log
def process_message(message, names, listen_socks):
    if all([message[DESTINATION] in names, names[message[DESTINATION]] in listen_socks]):
        send_message(names[message[DESTINATION]], message)
        LOGGER.info(f'A message has been sent to the user {message[DESTINATION]} from {message[SENDER]}.')

    elif all([message[DESTINATION] in names, names[message[DESTINATION]] not in listen_socks]):
        raise ConnectionError

    else:
        LOGGER.error(f'User {message[DESTINATION]} is not registered on the server.')


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


def main() -> None:
    ip_address, port = parse_args()

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((ip_address, port))
    server.settimeout(0.5)
    server.listen(MAX_CONNECTIONS)

    clients, messages, names = [], [], {}

    while True:
        try:
            client, client_address = server.accept()
            LOGGER.info(f'Connection established with {client_address}')
        except OSError:
            pass
        else:
            clients.append(client)

        recv_data_lst, send_data_lst, err_lst = [], [], []

        try:
            if clients:
                recv_data_lst, send_data_lst, err_lst = select.select(clients, clients, [], 0)
        except OSError:
            pass

        if recv_data_lst:
            for client_with_message in recv_data_lst:
                try:
                    process_client_message(
                        get_message(client_with_message), messages, client_with_message, clients, names
                    )
                except Exception as err:
                    LOGGER.error(f'{type(err).__name__}')
                    LOGGER.info(f'The client {client_with_message.getpeername()} disconnected from the server')
                    clients.remove(client_with_message)

        for message in messages:
            try:
                process_message(message, names, send_data_lst)
            except Exception as err:
                LOGGER.error(f'{type(err).__name__}')
                LOGGER.info(f'Communication with a client "{message[DESTINATION]}" has been lost')
                clients.remove(names[message[DESTINATION]])
                del names[message[DESTINATION]]
        messages.clear()

        # if messages and send_data_lst:
        #     sender, message_text = messages.pop(0)
        #     message = {
        #         ACTION: MESSAGE,
        #         SENDER: sender,
        #         TIME: time.time(),
        #         MESSAGE_TEXT: message_text
        #     }

        # for waiting_client in send_data_lst:
        #     try:
        #         send_message(waiting_client, message)
        #     except Exception as err:
        #         LOGGER.error(str(err))
        #         LOGGER.info(f'The client {waiting_client.getpeername()}  disconnected from the server')
        #         clients.remove(waiting_client)


if __name__ == '__main__':
    main()
