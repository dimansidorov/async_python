import json
from socket import socket

from .variables import MAX_PACKAGE_LENGTH, ENCODING

from typing import NoReturn


def get_message(s: socket) -> dict | NoReturn:
    encoded_message = s.recv(MAX_PACKAGE_LENGTH)
    if isinstance(encoded_message, bytes):
        response = json.loads(encoded_message.decode(ENCODING))
        if isinstance(response, dict):
            return response
    raise ValueError


def send_message(s: socket, message: dict) -> None:
    message = json.dumps(message)
    s.send(message.encode(ENCODING))
