class IncorrectDataRecivedError(Exception):
    def __str__(self):
        return 'An incorrect message was received from a remote computer.'


class ServerError(Exception):
    def __init__(self, text):
        self.text = text

    def __str__(self):
        return self.text


class NonDictInputError(Exception):
    def __str__(self):
        return 'The function argument must be a dictionary.'


class ReqFieldMissingError(Exception):
    def __init__(self, missing_field):
        self.missing_field = missing_field

    def __str__(self):
        return f'There is no required field in the accepted dictionary {self.missing_field}.'
