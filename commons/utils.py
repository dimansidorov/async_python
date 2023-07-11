import json
from socket import socket

from .variables import MAX_PACKAGE_LENGTH, ENCODING

from typing import NoReturn
from decorators import log


@log
def get_message(s: socket) -> dict | NoReturn:
    encoded_message = s.recv(MAX_PACKAGE_LENGTH)
    if isinstance(encoded_message, bytes):
        response = json.loads(encoded_message.decode(ENCODING))
        if isinstance(response, dict):
            return response
    raise ValueError


@log
def send_message(s: socket, message: dict) -> None:
    if isinstance(message, dict):
        message = json.dumps(message)
        e_message = message.encode(ENCODING)
        s.send(e_message)
    else:
        raise TypeError


@log
def check_port(port):
    return 1023 < port < 65536


@log
def check_mode(mode):
    return mode in ('send', 'listen')
