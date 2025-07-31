import json 
from flask import Blueprint, request, jsonify
from backend.services.server import get_updates_info,get_disk_info
from backend.middleware.jwt_validations import authorize
from backend.exceptions.APIException import InvalidRequestError
from backend.exceptions.JWTExeptions import TokenClaimsMismatch
import backend.utils.helpers as message

app_win_bp = Blueprint('server',__name__, url_prefix='/server')
    
@app_win_bp.route('/updates', methods=['POST'])
# @authorize
def updates():
    try:
        if request.json is None:
            raise InvalidRequestError()
        if 'server_name' not in request.json:
            raise TokenClaimsMismatch()
        
        server_name = request.json['server_name']
        
        serverStats = get_updates_info(server_name)
        if not serverStats:
            return message.error_response(f'Failed to retrive stats for server: {server_name}',404)
        serverStats ={k: json.loads(v) for k, v in serverStats.items()}
        return message.success_response(serverStats)
        
    except InvalidRequestError as e:
        return message.error_response(str(e.message))
    except TokenClaimsMismatch as e:
        return message.error_response(str(e.message))
    except Exception as e:
        return message.error_response(f'connect: {str(e)}')
    
    
@app_win_bp.route('/disk', methods=['POST'])
# @authorize
def disk():
    try:
        if request.json is None:
            raise InvalidRequestError()
        if 'server_name' not in request.json:
            raise TokenClaimsMismatch()
        
        server_name = request.json['server_name']
        
        serverStats = get_disk_info(server_name)
        if not serverStats:
            return message.error_response(f'Failed to retrive stats for server: {server_name}',404)
        serverStats ={k: json.loads(v) for k, v in serverStats.items()}
        return message.success_response(serverStats)
        
    except InvalidRequestError as e:
        return message.error_response(str(e.message))
    except TokenClaimsMismatch as e:
        return message.error_response(str(e.message))
    except Exception as e:
        return message.error_response(f'connect: {str(e)}')
    
@app_win_bp.route('/sql', methods=['POST'])
# @authorize
def sql_services():
    try:
        if request.json is None:
            raise InvalidRequestError()
        if 'server_name' not in request.json:
            raise TokenClaimsMismatch()
        
        server_name = request.json['server_name']
        
        serverStats = get_disk_info(server_name)
        if not serverStats:
            return message.error_response(f'Failed to retrive stats for server: {server_name}',404)
        serverStats ={k: json.loads(v) for k, v in serverStats.items()}
        return message.success_response(serverStats)
        
    except InvalidRequestError as e:
        return message.error_response(str(e.message))
    except TokenClaimsMismatch as e:
        return message.error_response(str(e.message))
    except Exception as e:
        return message.error_response(f'connect: {str(e)}')
    