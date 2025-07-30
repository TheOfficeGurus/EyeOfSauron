class UserExceptions(Exception):
    def __init__(self, message):
        self.message = message


class UserADNoUpdatedException(UserExceptions):
    def __init__(self, message):
        self.message = message


class UserNotFoundException(UserExceptions):
    def __init__(self, message):
        super().__init__("User not found")
