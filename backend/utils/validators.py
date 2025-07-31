import re
from email_validator import validate_email, EmailNotValidError

class Validators:
    @staticmethod
    def validate_email(email):
        try:
            validate_email(email)
            return True
        except EmailNotValidError:
            return False
    
    @staticmethod
    def validate_password(password):
        return len(password) >= 8 and re.search(r'[A-Z]', password)