class APIException(Exception):
    def __init__(self, message, status_code=400):
        self.message = message
        self.status_code = status_code


class InvalidCredentials(APIException):
    def __init__(self):
        super().__init__("Invalid credentials", 401)


class InvalidRequestError(APIException):
    def __init__(self):
        super().__init__("Invalid request", 400)
