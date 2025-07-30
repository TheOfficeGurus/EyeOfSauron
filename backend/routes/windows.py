import json 
from flask import Blueprint, request, jsonify
# from backend.services.windows_service import connect_to_sql_server,get_server_stats, get_linux_stats_ssh
from backend.services.windows_service import get_linux_stats_ssh
from backend.middleware.jwt_validations import authorize
from backend.exceptions.APIException import InvalidRequestError
from backend.exceptions.JWTExeptions import TokenClaimsMismatch
import backend.utils.helpers as message

app_win_bp = Blueprint('windows',__name__, url_prefix='/windwows')

# @app_win_bp.route('/stats', methods=['POST'])
# @authorize
# def stats():
#     try:
#         if request.json is None:
#             raise InvalidRequestError()
#         if 'server_name' not in request.json:
#             raise TokenClaimsMismatch()
        
#         server_name = request.json['server_name']
#         wmi_conn = connect_to_sql_server(server_name)
        
#         if not wmi_conn:
#             return message.error_response(f"Failed to conect to server: {server_name}",404)
        
#         serverStats = get_server_stats(wmi_conn)
#         if not serverStats:
#             return message.error_response(f'Failed to retrive stats for server: {server_name}',404)
        
#         return message.success_response(serverStats)
        
#     except InvalidRequestError as e:
#         return message.error_response(str(e.message))
#     except TokenClaimsMismatch as e:
#         return message.error_response(str(e.message))
#     except Exception as e:
#         return message.error_response(f'connect: {str(e.message)}')
    
    
@app_win_bp.route('/test', methods=['GET'])
def test():
    try:
        c = get_linux_stats_ssh('localhost','usr','pw')
        return message.success_response(c)
    except Exception as e:
        return message.error_response(f'Error retiving stats:{str(e)}',500)