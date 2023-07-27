import socket
import sys
import argparse
import logging
import select
import threading
import logs.config_server_logs
from commons.variables import *
from commons.utils import *
from decorators import log
from descriptiors import Port
from metaclasses import ServerVerifier
from server_database import ServerStorage

logger = logging.getLogger('server')


@log
def arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-a', default='', nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    listen_address = namespace.a
    listen_port = namespace.p
    return listen_address, listen_port


class Server(threading.Thread, metaclass=ServerVerifier):
    port = Port()

    def __init__(self, listen_address, listen_port, database):
        self.addr = listen_address
        self.port = listen_port
        self.database = database
        self.clients = []
        self.messages = []
        self.names = dict()
        self.sock = None
        super().__init__()

    def init_socket(self):
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.bind((self.addr, self.port))
        transport.settimeout(0.5)

        self.sock = transport
        self.sock.listen()

    def run(self):
        self.init_socket()
        while True:
            try:
                client, client_address = self.sock.accept()
            except OSError:
                pass
            else:
                logger.info(f'The connection to the PC is established {client_address}')
                self.clients.append(client)

            recv_data_lst = []
            send_data_lst = []
            err_lst = []
            try:
                if self.clients:
                    recv_data_lst, send_data_lst, err_lst = select.select(self.clients, self.clients, [], 0)
            except OSError:
                pass

            if recv_data_lst:
                for client_with_message in recv_data_lst:
                    try:
                        self.process_client_message(get_message(client_with_message), client_with_message)
                    except:
                        logger.info(f'Client {client_with_message.getpeername()} disconnected from the server.')
                        self.clients.remove(client_with_message)

            for message in self.messages:
                try:
                    self.process_message(message, send_data_lst)
                except:
                    logger.info(f'Communication with a client named {message[DESTINATION]} has been lost')
                    self.clients.remove(self.names[message[DESTINATION]])
                    del self.names[message[DESTINATION]]
            self.messages.clear()

    def process_message(self, message, listen_socks):
        if all([message[DESTINATION] in self.names, self.names[message[DESTINATION]] in listen_socks]):
            send_message(self.names[message[DESTINATION]], message)
            logger.info(f'A message was sent to the user {message[DESTINATION]} from the user {message[SENDER]}.')

        elif all([message[DESTINATION] in self.names, self.names[message[DESTINATION]] not in listen_socks]):
            raise ConnectionError

        else:
            logger.error(
                f'The user {message[DESTINATION]} is not registered on the server, sending the message is not possible.'
            )

    def process_client_message(self, message, client):
        if all([
            ACTION in message,
            message[ACTION] == PRESENCE,
            TIME in message,
            USER in message
        ]):
            if message[USER][ACCOUNT_NAME] not in self.names.keys():
                self.names[message[USER][ACCOUNT_NAME]] = client
                client_ip, client_port = client.getpeername()
                self.database.user_login(message[USER][ACCOUNT_NAME], client_ip, client_port)
                send_message(client, RESPONSE_200)
            else:
                response = RESPONSE_400
                response[ERROR] = 'The username is already taken.'
                send_message(client, response)
                self.clients.remove(client)
                client.close()

        elif all([
            ACTION in message,
            message[ACTION] == MESSAGE,
            DESTINATION in message,
            TIME in message,
            SENDER in message,
            MESSAGE_TEXT in message
        ]):
            self.messages.append(message)

        elif all([
            ACTION in message,
            message[ACTION] == EXIT,
            ACCOUNT_NAME in message
        ]):
            self.database.user_logout(message[ACCOUNT_NAME])
            self.clients.remove(self.names[message[ACCOUNT_NAME]])
            self.names[message[ACCOUNT_NAME]].close()
            del self.names[message[ACCOUNT_NAME]]

        else:
            response = RESPONSE_400
            response[ERROR] = 'Incorrect request'
            send_message(client, response)


def print_help():
    print(
        'Commands: \n'
        'users or u - list of users \n'
        'connected or c - list of connected users \n'
        'loghist or l - users login history \n'
        'exit or q - shutting down the server \n'
        'help or h - help output for supported commands \n'
    )


def main():
    listen_address, listen_port = arg_parser()
    database = ServerStorage()
    server = Server(listen_address, listen_port, database)
    server.daemon = True
    server.start()

    print_help()

    while True:
        command = input('Enter the command: ')
        if command in ('help', 'h'):
            print_help()
        elif command in ('exit', 'q'):
            break
        elif command in ('users', 'u'):
            for user in sorted(database.users_list()):
                print(f'User {user[0]}, last login: {user[1]}')
        elif command in ('connected', 'c'):
            for user in sorted(database.active_users_list()):
                print(f'User {user[0]}, connected: {user[1]}:{user[2]}, connection setup time: {user[3]}')
        elif command in ('loghist', 'l'):
            name = input(
                'Enter the username to view the history or just press Enter to display the entire history: ')
            for user in sorted(database.login_history(name)):
                print(f'User: {user[0]} connection setup time: {user[1]}. connected: {user[2]}:{user[3]}')
        else:
            print('Incorrect command')


if __name__ == '__main__':
    main()
