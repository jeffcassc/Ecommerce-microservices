from flask import Blueprint, request, jsonify
from app.services.user_service import UserService
from bson import ObjectId
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

user_bp = Blueprint('user', __name__, url_prefix='/api/users')

@user_bp.route('/register', methods=['POST'])
def register():
    try:
        # Verificar que el contenido es JSON
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400
            
        data = request.get_json(force=True)  # force=True para manejar mejor los errores
        
        logger.info(f"Received registration data: {data}")
        
        # Validar campos mínimos
        required_fields = ['name', 'last_name', 'email', 'password']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400
            
        # Convertir lastName a last_name si existe
        if 'lastName' in data:
            data['last_name'] = data.pop('lastName')
        
        user = UserService.register_user(data)
        return jsonify({
            "message": "User registered successfully",
            "user_id": str(user['_id']),
            "user_uuid": user['user_id']
        }), 201
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Unexpected error in registration: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500
@user_bp.route('/<user_id>', methods=['GET'])
def get_user(user_id):
    try:
        user = UserService.get_user(user_id)
        user['_id'] = str(user['_id'])  # Convert ObjectId to string
        return jsonify(user), 200
    except ValueError as e:
        logger.error(f"Error getting user: {str(e)}")
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        logger.error(f"Unexpected error getting user: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500

@user_bp.route('/', methods=['GET'])
def get_all_users():
    try:
        users = UserService.get_all_users()
        for user in users:
            user['_id'] = str(user['_id'])  # Convert ObjectId to string
        return jsonify(users), 200
    except Exception as e:
        logger.error(f"Error getting all users: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500

@user_bp.route('/<user_id>', methods=['PUT'])
def update_user(user_id):
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        user = UserService.update_user(user_id, data)
        user['_id'] = str(user['_id'])  # Convert ObjectId to string
        return jsonify({
            "message": "User updated successfully",
            "user": user
        }), 200
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Error updating user: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500

@user_bp.route('/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        result = UserService.delete_user(user_id)
        return jsonify(result), 200
    except ValueError as e:
        logger.error(f"Error deleting user: {str(e)}")
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        logger.error(f"Error deleting user: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500

@user_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        result = UserService.login_user(data)
        return jsonify(result), 200
    except ValueError as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({"error": str(e)}), 401
    except Exception as e:
        logger.error(f"Unexpected login error: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500