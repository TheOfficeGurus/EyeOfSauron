from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import json
import time 
from flask import Blueprint, request, jsonify
from backend.services.server import get_all_server_info_optimized, get_updates_info,get_disk_info,get_sql_services_info,get_memory_info
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
        return message.error_response(f'updates: {str(e)}')
    
    
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
        if serverStats: #type: ignore #vscode Hint
            msg =serverStats['disk']
        else:
            msg= str(e)
        return message.error_response(f'disk: {msg}')
    
@app_win_bp.route('/sql', methods=['POST'])
# @authorize
def sql_services():
    try:
        if request.json is None:
            raise InvalidRequestError()
        if 'server_name' not in request.json:
            raise TokenClaimsMismatch()
        
        server_name = request.json['server_name']
        
        serverStats = get_sql_services_info(server_name)
        if not serverStats:
            return message.error_response(f'Failed to retrive stats for server: {server_name}',404)
        serverStats ={k: json.loads(v) for k, v in serverStats.items()}
        return message.success_response(serverStats)
        
    except InvalidRequestError as e:
        return message.error_response(str(e.message))
    except TokenClaimsMismatch as e:
        return message.error_response(str(e.message))
    except Exception as e:
        return message.error_response(f'sql_services: {str(e)}')
@app_win_bp.route('/memory', methods=['POST'])
# @authorize
def get_memoryInfo():
    try:
        if request.json is None:
            raise InvalidRequestError()
        if 'server_name' not in request.json:
            raise TokenClaimsMismatch()
        
        server_name = request.json['server_name']
        
        serverStats = get_memory_info(server_name)
        if not serverStats:
            return message.error_response(f'Failed to retrive stats for server: {server_name}',404)
        serverStats ={k: json.loads(v) for k, v in serverStats.items()}
        return message.success_response(serverStats)
        
    except InvalidRequestError as e:
        return message.error_response(str(e.message))
    except TokenClaimsMismatch as e:
        return message.error_response(str(e.message))
    except Exception as e:
        return message.error_response(f'get_memoryInfo: {str(e)}')

@app_win_bp.route('/batch/optimized', methods=['POST'])
def batch_optimized():
    """Endpoint optimizado que obtiene toda la información en una sola consulta por servidor"""
    try:
        if request.json is None:
            raise InvalidRequestError()
        if 'servers' not in request.json:
            raise TokenClaimsMismatch()
        
        servers = request.json['servers']
        if not isinstance(servers, list):
            return message.error_response("'servers' must be a list")
        
        def fetch_optimized_data(server_name):
            try:
                start_time = time.time()
                data = get_all_server_info_optimized(server_name)
                end_time = time.time()
                
                if data:
                    return {
                        'server': server_name,
                        'data': data,
                        'success': True,
                        'response_time': round(end_time - start_time, 2),
                        'timestamp': datetime.now().isoformat()
                    }
                else:
                    return {
                        'server': server_name,
                        'data': None,
                        'success': False,
                        'error': 'Failed to retrieve data',
                        'response_time': round(end_time - start_time, 2)
                    }
            except Exception as e:
                return {
                    'server': server_name,
                    'data': None,
                    'success': False,
                    'error': str(e),
                    'response_time': 0
                }
        
        # Ejecutar en paralelo con límite de workers
        results = []
        start_total = time.time()
        
        with ThreadPoolExecutor(max_workers=3) as executor:  # Reducido para evitar sobrecarga
            future_to_server = {executor.submit(fetch_optimized_data, server): server for server in servers}
            
            for future in as_completed(future_to_server):
                try:
                    result = future.result(timeout=150)  # 2.5 minutos por servidor
                    results.append(result)
                except Exception as e:
                    server = future_to_server[future]
                    results.append({
                        'server': server,
                        'data': None,
                        'success': False,
                        'error': f"Execution timeout or error: {str(e)}",
                        'response_time': 0
                    })
        
        end_total = time.time()
        
        return message.success_response({
            'servers_data': results,
            'total_servers': len(servers),
            'successful_servers': len([r for r in results if r['success']]),
            'total_time': round(end_total - start_total, 2),
            'average_time': round((end_total - start_total) / len(servers), 2),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return message.error_response(f'batch_optimized: {str(e)}')
