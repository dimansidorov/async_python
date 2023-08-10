"""Errors"""


class ServerError(Exception):
    """
    Exception class, for handling server errors.
    When generating, it requires a string with a description of the error,
    received from the server.
    """

    def __init__(self, text):
        self.text = text

    def __str__(self):
        return self.text
