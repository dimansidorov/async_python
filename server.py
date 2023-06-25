import json
import socket
import sys
from commons.variables import DEFAULT_PORT, RESPONSE, PRESENCE, ACTION, TIME, USER, ACCOUNT_NAME, ERROR, MAX_CONNECTIONS
from commons.utils import get_message, send_message


def parse_client_message(message) -> dict:
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
            raise ValueError
        else:
            return listen_port
    except IndexError:
        print("После параметра -'p' указывается номер порта.")
        sys.exit(1)
    except ValueError:
        print('Порт - это число в диапазоне от 1024 до 65535.')
        sys.exit(1)


def get_ip_address():
    try:
        if '-a' in sys.argv:
            listen_address = sys.argv[sys.argv.index('-a') + 1]
        else:
            listen_address = ''
    except IndexError:
        print("После параметра 'a'- адрес, который будет слушать сервер.")
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
        try:
            message_from_client = get_message(client)
            print(message_from_client)
            response = parse_client_message(message_from_client)
            send_message(client, response)
            client.close()
            break
        except (ValueError, json.JSONDecodeError):
            print('Некорретное сообщение от клиента.')
            client.close()
            break


if __name__ == '__main__':
    main()
