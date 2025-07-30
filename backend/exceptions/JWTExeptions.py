class JWTExeptions(Exception):
    def __init__(self, message):
        self.message = message

class TokenExpired(JWTExeptions):
    def __init__(self):
        super().__init__("Token expired")
        
class TokenInvalidAuth(JWTExeptions):
    def __init__(self):
        super().__init__("Authorization header missing or invalid token")
class TokenClaimsMismatch(JWTExeptions):
    def __init__(self):
        super().__init__("Unauthorized: claim mismatch")
        