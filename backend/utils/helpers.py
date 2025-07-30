from flask import jsonify

def success_response(data, message="Success"):
    return jsonify({
        'success': True,
        'message': message,
        'data': data
    }),200

def error_response(message, status_code=400):
    return jsonify({
        'success': False,
        'error': message
    }), status_code

