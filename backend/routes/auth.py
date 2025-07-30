import json
from flask import Blueprint, request, jsonify
from backend.services.auth_service import AuthService
from backend.middleware.jwt_validations import authorize
from backend.exceptions.APIException import InvalidRequestError
from backend.exceptions.JWTExeptions import TokenClaimsMismatch
import backend.utils.helpers as message

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['POST'])
# @authorize()
def login():
    try:
        if request.json is None:
            raise InvalidRequestError()
        if [key for key in request.json if key not in ['service', 'environment', 'phrase']]:
            raise TokenClaimsMismatch()
        
    ### validate user cretentials here
    ##TODO: implement user validation logic with database 
    
        token = AuthService.generate_token(request.json)
        
    except InvalidRequestError as e:
        return message.error_response(str(e.message))
    except TokenClaimsMismatch as e:
        return message.error_response(str(e.message))
    except Exception as e:
        return message.error_response(f'login: {str(e)}',500)
    return jsonify({"token": f'Bearer {token}'}),200

@auth_bp.route('/verify',methods=['POST'])
@authorize(required_claims={'service': 'ATS'})
def verify():
    return message.success_response("Token is valid")