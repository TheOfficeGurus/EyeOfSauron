import datetime
import json
from functools import wraps
from flask import request, jsonify
from dateutil import parser
from authlib.jose import JsonWebEncryption as jwe
from backend.exceptions.JWTExeptions import TokenExpired, TokenClaimsMismatch
from backend.utils.helpers import error_response
from backend.config import Config as app_config


def authorize(required_claims=None):
    def jwt_required(f):
        @wraps(f)
        def decorated_wrapper(*args, **kwargs):
            auth_header = request.headers.get('Authorization',"")
            if not auth_header:
                return error_response('Token missing',401)
                # raise TokenInvalidAuth()
            if "Bearer" not in auth_header:
                return error_response('Token incompleted or missing',401)
                # raise TokenInvalidAuth()
            token = auth_header.split(" ")[2]
            try:
                payload = jwe().deserialize_compact(token, app_config._KEY_)
                data = json.loads(payload['payload'].decode())
                if required_claims:
                    for k, v in required_claims.items():
                        if data.get(k) != v:
                            raise TokenClaimsMismatch()
                if 'exp' in data:
                    exp = parser.parse(data['exp'])
                    if datetime.datetime.now(tz=datetime.timezone.utc) > exp:
                        raise TokenExpired()
            # except TokenInvalidAuth as e:
            #     return jsonify({'error': f'{e.message}'}), 401
            except TokenExpired as e:
                return error_response(str(e.message),401)
            except TokenClaimsMismatch as e:
                return error_response(str(e.message),403)
            except Exception as e:
                return error_response(f' invalid token: {str(e)}',500)
                
            return f(*args, **kwargs)
        return decorated_wrapper
    return jwt_required