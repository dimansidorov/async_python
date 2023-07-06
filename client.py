import json
import socket
import sys
import time

from commons.utils import send_message, get_message
from commons.variables import ACCOUNT_NAME, ACTION, DEFAULT_PORT, DEFAULT_IP_ADDRESS, ERROR, PRESENCE, RESPONSE, TIME, \
    USER

import logging
import logs.config_client_logs

CLIENT_LOGGER = logging.getLogger('client')


def create_presence_msg(account_name='Guest'):
    out = {
        ACTION: PRESENCE,
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: account_name
        }
    }
    return out


def get_answer_server(message):
    CLIENT_LOGGER.info('getting answer from server')
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            return '200 : OK'
        return f'400 : {message[ERROR]}'
    raise ValueError


def main():
    try:
        server_address = sys.argv[1]
        server_port = int(sys.argv[2])
        if server_port < 1024 or server_port > 65535:
            raise ValueError
    except IndexError:
        server_address = DEFAULT_IP_ADDRESS
        server_port = DEFAULT_PORT
    except ValueError:
        CLIENT_LOGGER.critical(f'Uncorrected port - {server_port}. Port - is a number from 1024 to 65535.')
        sys.exit(1)
    finally:
        CLIENT_LOGGER.info(f'server address - {server_address}, server port - {server_port}')


    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((server_address, server_port))
    message_to_server = create_presence_msg()
    send_message(client, message_to_server)
    try:
        answer = get_answer_server(get_message(client))
    except json.JSONDecodeError:
        CLIENT_LOGGER.error(f'Error decoding json string')
    except ValueError:
        CLIENT_LOGGER.error('Error!')
    else:
        CLIENT_LOGGER.info(f'Answer - {answer}')


if __name__ == '__main__':
    main()
