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
    DESTINATION,
    ERROR,
    EXIT,
    MESSAGE,
    MESSAGE_TEXT,
    PRESENCE,
    SENDER,
    RESPONSE,
    TIME,
    USER
)
import errors
import logging
import logs.config_client_logs
from decorators import log

LOGGER = logging.getLogger('client')


@log
def create_exit_message(account_name):
    return {
        ACTION: EXIT,
        TIME: time.time(),
        ACCOUNT_NAME: account_name
    }


@log
def get_message_from_server(s: socket, username: str):
    while True:
        try:
            message = get_message(s)
            if all([
                ACTION in message,
                message[ACTION] == MESSAGE,
                SENDER in message,
                MESSAGE_TEXT in message,
                message[DESTINATION] == username
            ]):
                LOGGER.info('Received a message from the user'
                            f'{message[SENDER]}:{message[MESSAGE_TEXT]}')
                print(f'{message[SENDER]}: {message[MESSAGE_TEXT]}')
            else:
                LOGGER.error(f'Received an invalid massage')
        except errors.IncorrectDataError:
            LOGGER.error(f'Received an incorrect data')
        except (ConnectionError, OSError, ConnectionResetError, ConnectionAbortedError, json.JSONDecodeError):
            LOGGER.critical(f'Connection to the server is lost')
            break


@log
def print_help():
    print(f' You can use the following commands: \n'
          f'"message" or "1" - send a message; \n'
          f'"help" or "2" - get a hint on commands; \n'
          f'"exit" or "3" - finish the program;')


@log
def interact_with_user(s: socket, username: str):
    print(f'Hello, {username}.\n')
    print_help()
    while True:
        command = input('Enter the command: \n')
        if command in ('1', 'message'):
            create_message(s, username)
        elif command in ('2', 'help'):
            print_help()
        elif command in ('3', 'exit'):
            send_message(s, create_exit_message(username))
            LOGGER.info('Connection termination')
            time.sleep(0.5)
            break
        else:
            print('Incorrect command.')
            print_help()


@log
def create_message(s, account_name='Guest'):
    recipient = input('Enter a recipient of message: ')
    message = input('Enter a message to send:  ')
    message_dict = {
        ACTION: MESSAGE,
        SENDER: account_name,
        DESTINATION: recipient,
        TIME: time.time(),
        MESSAGE_TEXT: message
    }
    LOGGER.info('A message has been generated')
    try:
        send_message(s, message_dict)
        LOGGER.info(f'Send a message to {recipient}')
    except Exception as err:
        LOGGER.error(f'{err.__name__}')
        LOGGER.critical('The connection is lost')
        sys.exit(1)


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
    parser.add_argument('port', default=DEFAULT_PORT, type=int, nargs='?')
    # parser.add_argument('-m', '--mode', default='listen', nargs='?')
    parser.add_argument('-n', '--name', default=None, nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    server_address = namespace.addr
    server_port = namespace.port
    # client_mode = namespace.mode
    client_name = namespace.name
    if not check_port(server_port):
        LOGGER.critical(f'Invalid port -  {server_port}.')
        sys.exit(1)

    # if not check_mode(client_mode):
    #     LOGGER.critical(
    #         f'Invalid mode -  {client_mode}.')
    #     sys.exit(1)

    return server_address, server_port, client_name


def main():
    server_address, server_port, client_name = parse_args()

    if not client_name:
        client_name = input('Enter the username: ')

    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((server_address, server_port))
        send_message(client, create_presence_msg(client_name))
        answer = get_process_response_ans(get_message(client))
        LOGGER.info(f'{answer}')
    except json.JSONDecodeError:
        LOGGER.error(f'Error decoding json string')
        sys.exit(1)
    except (ConnectionRefusedError, ConnectionError):
        LOGGER.critical(f'Failed to connect to the server {server_address}:{server_port}')
        sys.exit(1)
    except Exception as err:
        LOGGER.error(f'Error! {err.__name__}')
        sys.exit(1)
    else:
        receiver = threading.Thread(target=get_message_from_server, args=(client, client_name))
        receiver.daemon = True
        receiver.start()

        user_interface = threading.Thread(target=interact_with_user, args=(client, client_name))
        user_interface.daemon = True
        user_interface.start()

        while True:
            time.sleep(1)
            if not(receiver.is_alive() and user_interface.is_alive()):
                break


        # while True:
        #     try:
        #         if client_mode == 'listen':
        #             message = get_message_from_server(get_message(client))
        #         else:
        #             send_message(client, create_message(client))
        #     except Exception as err:
        #         LOGGER.error(f'The connection to the {server_address} server has been lost. Error: {err}')
        #         sys.exit(1)


if __name__ == '__main__':
    main()
