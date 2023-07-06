import json
import socket
import sys
from commons.variables import DEFAULT_PORT, RESPONSE, PRESENCE, ACTION, TIME, USER, ACCOUNT_NAME, ERROR, MAX_CONNECTIONS
from commons.utils import get_message, send_message
import logging
import logs.config_server_logs

SERVER_LOGGER = logging.getLogger('server')


def parse_client_message(message) -> dict:
    SERVER_LOGGER.debug(f'Parse message from client: {message}')
    if all([ACTION in message, message[ACTION] == PRESENCE, TIME in message,
            USER in message, message[USER][ACCOUNT_NAME] == 'Guest']):
        return {RESPONSE: 200}
    return {
        RESPONSE: 400,
        ERROR: 'Bad Request'
    }


def get_port() -> int:
    try:
        if '-p' in sys.argv:
            listen_port = int(sys.argv[sys.argv.index('-p') + 1])
        else:
            listen_port = DEFAULT_PORT
        if listen_port < 1024 or listen_port > 65535:
            SERVER_LOGGER.critical(f'Uncorrected port - {listen_port}. Port - is a number from 1024 to 65535.')
            raise ValueError
        else:
            SERVER_LOGGER.info(f'Server started. port - {listen_port}')
            return listen_port
    except IndexError:
        SERVER_LOGGER.critical("After -'p' please enter port")
        sys.exit(1)
    except ValueError:
        sys.exit(1)


def get_ip_address():
    try:
        if '-a' in sys.argv:
            listen_address = sys.argv[sys.argv.index('-a') + 1]
            SERVER_LOGGER.info(f'IP address - {listen_address}')
        else:
            listen_address = ''
            SERVER_LOGGER.info('Address is not specified, connections from any addresses are accepted.')
    except IndexError:
        SERVER_LOGGER.critical(f'Uncorrected address. After parameter "a" please enter address, '
                               f'which server will listen.')
        sys.exit(1)
    else:
        return listen_address


def main() -> None:
    port = get_port()
    ip_address = get_ip_address()
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((ip_address, port))
    server.listen(MAX_CONNECTIONS)
    while True:
        client, client_address = server.accept()
        SERVER_LOGGER.info(f'Connection established with {client_address}')
        try:
            message_from_client = get_message(client)
            SERVER_LOGGER.debug(f'Message received {message_from_client}')
            response = parse_client_message(message_from_client)
            send_message(client, response)
        except json.JSONDecodeError:
            SERVER_LOGGER.error(f'Error decoding json string')
        except ValueError:
            SERVER_LOGGER.error(f'Error!')
        finally:
            SERVER_LOGGER.debug(f'Connection with {client_address} is closing.')
            client.close()


if __name__ == '__main__':
    main()
