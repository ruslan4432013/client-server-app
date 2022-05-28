class IncorrectDataRecivedError(Exception):
    """Exception - invalid data received from socket"""
    def __str__(self):
        return 'Invalid message received from remote computer.'


class ServerError(Exception):
    """Exception - server error"""
    def __init__(self, text):
        self.text = text

    def __str__(self):
        return self.text


class NonDictInputError(Exception):
    """Exception - function argument is not a dictionary"""
    def __str__(self):
        return 'The function argument must be a dictionary.'


class ReqFieldMissingError(Exception):
    """Error - missing required field in received dictionary"""
    def __init__(self, missing_field):
        self.missing_field = missing_field

    def __str__(self):
        return f'Received dictionary is missing a required field {self.missing_field}.'
