import json
from socket import socket

from .variables import MAX_PACKAGE_LENGTH, ENCODING

from typing import NoReturn
from commons.decorators import log


@log
def get_message(sock: socket) -> dict | NoReturn:
    """
    The function of receiving messages from remote computers.
    Accepts JSON messages, decodes the received message
    and checks that the dictionary has been received.
    :param sock:
    :return:
    """
    encoded_message = sock.recv(MAX_PACKAGE_LENGTH)
    if isinstance(encoded_message, bytes):
        response = json.loads(encoded_message.decode(ENCODING))
        if isinstance(response, dict):
            return response
    raise ValueError


@log
def send_message(sock: socket, message: dict) -> None:
    """
    The function of sending dictionaries via socket.
    Encodes the dictionary in JSON format and sends it via socket.
    :param sock:
    :param message:
    :return:
    """
    if isinstance(message, dict):
        message = json.dumps(message)
        e_message = message.encode(ENCODING)
        sock.send(e_message)
    else:
        raise TypeError


@log
def check_port(port):
    return 1023 < port < 65536
