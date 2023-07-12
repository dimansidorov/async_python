import time
import select
import socket
import sys
import argparse
from commons.variables import (
    ACCOUNT_NAME,
    ACTION,
    DEFAULT_PORT,
    ERROR,
    MAX_CONNECTIONS,
    MESSAGE,
    MESSAGE_TEXT,
    PRESENCE,
    RESPONSE,
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
def process_client_message(message, messages_list, client) -> None:
    LOGGER.debug(f'Разбор сообщения от клиента : {message}')
    # Если это сообщение о присутствии, принимаем и отвечаем, если успех
    if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
            and USER in message and message[USER][ACCOUNT_NAME] == 'Guest':
        send_message(client, {RESPONSE: 200})
        return
    # Если это сообщение, то добавляем его в очередь сообщений. Ответ не требуется.
    elif ACTION in message and message[ACTION] == MESSAGE and \
            TIME in message and MESSAGE_TEXT in message:
        messages_list.append((message[ACCOUNT_NAME], message[MESSAGE_TEXT]))
        return
    # Иначе отдаём Bad request
    else:
        send_message(client, {
            RESPONSE: 400,
            ERROR: 'Bad Request'
        })
        return


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

    clients, messages = [], []

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
                    process_client_message(get_message(client_with_message), messages, client_with_message)
                except Exception as err:
                    LOGGER.error(f'{str(err)}')
                    LOGGER.info(f'The client {client_with_message.getpeername()} disconnected from the server')
                    clients.remove(client_with_message)

        if messages and send_data_lst:
            sender, message_text = messages.pop(0)
            message = {
                ACTION: MESSAGE,
                SENDER: sender,
                TIME: time.time(),
                MESSAGE_TEXT: message_text
            }

            for waiting_client in send_data_lst:
                try:
                    send_message(waiting_client, message)
                except Exception as err:
                    LOGGER.error(str(err))
                    LOGGER.info(f'The client {waiting_client.getpeername()}  disconnected from the server')
                    clients.remove(waiting_client)


if __name__ == '__main__':
    main()
