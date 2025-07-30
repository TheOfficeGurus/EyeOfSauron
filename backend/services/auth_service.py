import jwt
import json
import datetime
# from app.models.user import User
from backend.config import Config as app_config
from authlib.jose import JsonWebEncryption as jwe

class AuthService:
    
    @staticmethod    
    def generate_token(payload):
        
        protected_header = {
            "alg": "dir",
            "enc": "A256GCM"
        }
        
        token_json = json.loads(json.dumps(payload))
        token_json['exp'] = (datetime.datetime.now(tz=datetime.timezone.utc)+ datetime.timedelta(minutes=10)).isoformat()
        token_json['iat'] = (datetime.datetime.now(tz=datetime.timezone.utc)).isoformat()
        token_json['iss'] = f'CTRLPlayer for the galaxy'
        
        jwt_json = json.dumps(token_json).encode()
        jwt_token:str = jwe().serialize_compact(protected_header, jwt_json, app_config._KEY_).__str__().replace('b\'', '').replace("'", '')
        return jwt_token


    # def decode_jwt_token(token):
    #     """
    #     Function to decode a JWT token.
    #     """
    #     try:
    #         decrypted = jwe().deserialize_compact(token, app_config._KEY_)
    #         return json.loads(decrypted["payload"].decode())
    #     except Exception as e:
    #         print(f"Error decoding token: {e}")
    #         return None
        