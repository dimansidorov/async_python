import json
import socket
import sys
import threading
import time
import argparse

from commons.utils import send_message, get_message, check_port, check_mode
from commons.variables import (
    ACCOUNT_NAME,
    ACTION,
    DEFAULT_PORT,
    DEFAULT_IP_ADDRESS,
    ERROR,
    EXIT,
    MESSAGE,
    MESSAGE_TEXT,
    PRESENCE,
    SENDER,
    RESPONSE,
    TIME,
    USER, DESTINATION
)

import logging
import logs.config_client_logs
from decorators import log
from errors import ReqFieldMissingError, ServerError
from metaclasses import ClientVerifier

LOGGER = logging.getLogger('client')


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


class ClientSender(threading.Thread, metaclass=ClientVerifier):
    def __init__(self, account_name, sock):
        self.account_name = account_name
        self.sock = sock
        super().__init__()

    def create_exit_message(self):
        return {
            ACTION: EXIT,
            TIME: time.time(),
            ACCOUNT_NAME: self.account_name
        }

    @log
    def create_message(self):
        to_user = input("Enter the user: ")
        message = input('Enter the message: ')
        message_dict = {
            ACTION: MESSAGE,
            SENDER: self.account_name,
            DESTINATION: to_user,
            TIME: time.time(),
            MESSAGE_TEXT: message
        }
        try:
            send_message(self.sock, message_dict)
            LOGGER.info(f'A message has been sent to the user {to_user}')
        except Exception as err:
            LOGGER.critical(f'Connection to the server is lost. Error: {type(err).__name__}')
            sys.exit(1)

    def run(self):
        self.print_help()

        while True:
            command = input('Enter the command: ')
            if command in ('message', '1'):
                self.create_message()
            elif command in ('help', '2'):
                self.print_help()
            elif command in ('exit', '3'):
                try:
                    send_message(self.sock, self.create_exit_message())
                except:
                    pass
                LOGGER.info("Completion of work on the user's command.")

                time.sleep(0.5)
                break
            else:
                print('The command is not recognized, try again. help - output supported commands.')

    @staticmethod
    def print_help():
        print('Choose the command:')
        print('message or 1 - send a message.')
        print('help or 2 - output hints by commands')
        print('exit or 3 - exit')


class ClientReader(threading.Thread, metaclass=ClientVerifier):
    def __init__(self, account_name, sock):
        self.account_name = account_name
        self.sock = sock
        super().__init__()

    def run(self):
        while True:
            try:
                message = get_message(self.sock)
                if all([ACTION in message, message[ACTION] == MESSAGE, SENDER in message, DESTINATION in message,
                        MESSAGE_TEXT in message, message[DESTINATION] == self.account_name]):

                    LOGGER.info(f'Received a message from the {message[SENDER]}:'
                                f'\n{message[MESSAGE_TEXT]}')
                else:
                    LOGGER.error(f'Incorrect message from server: {message}')

            except (OSError, ConnectionError, ConnectionAbortedError,
                    ConnectionResetError, json.JSONDecodeError):
                LOGGER.critical(f'Lost connection')
                break

            except Exception as err:
                LOGGER.error(f'Error: {type(err).__name__}')


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


def main():
    server_address, server_port, client_name = parse_args()

    if not client_name:
        client_name = input('Enter the username: ')

    LOGGER.info(
        f'The client is running with the following parameters: server address: {server_address}, '
        f'port: {server_port}, username: {client_name}')

    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.connect((server_address, server_port))
        send_message(server, create_presence_msg(client_name))
        answer = get_process_response_ans(get_message(server))
        LOGGER.info(f'A connection to the server has been established. Server response: {answer}')
        print(f'A connection to the server has been established.')

    except json.JSONDecodeError:
        LOGGER.error('Failed to decode the received Json string.')
        sys.exit(1)

    except ServerError as error:
        LOGGER.error(f'When establishing a connection, the server returned an error: {error.text}')
        sys.exit(1)

    except ReqFieldMissingError as missing_error:
        LOGGER.error(f'The required field is missing in the server response {missing_error.missing_field}')
        sys.exit(1)

    except (ConnectionRefusedError, ConnectionError):
        LOGGER.critical(
            f'Failed to connect to the server {server_address}:{server_port}, '
            f'the destination computer rejected the connection request.')
        sys.exit(1)

    else:
        module_receiver = ClientReader(client_name, server)
        module_receiver.daemon = True
        module_receiver.start()

        module_sender = ClientSender(client_name, server)
        module_sender.daemon = True
        module_sender.start()

        while True:
            time.sleep(1)
            if module_receiver.is_alive() and module_sender.is_alive():
                continue
            break


if __name__ == '__main__':
    main()
