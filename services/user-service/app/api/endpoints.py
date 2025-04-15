from flask import Blueprint, request, jsonify
from werkzeug.exceptions import BadRequest, NotFound, InternalServerError
from app.models.user_models import UserCreate, UserUpdate, UserInDB
from app.services.user_service import UserService
from app.services.mongo_service import mongo_service
import logging
from bson import ObjectId
from datetime import datetime

logger = logging.getLogger(__name__)

bp = Blueprint('user_api', __name__, url_prefix='/api/users')

@bp.route('/', methods=['POST'])
def create_user():
    try:
        data = request.get_json()
        user_data = UserCreate(**data).dict()
        
        # En producción, aquí deberías hashear la contraseña
        user_id = mongo_service.create_user(user_data)
        
        # Publicar evento de registro (simplificado)
        registration_event = {
            "event_type": "USER_REGISTERED",
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "email": user_data['email']
        }
        # Aquí iría la publicación a Kafka en una implementación real
        
        return jsonify({"id": user_id}), 201
    except ValueError as e:
        raise BadRequest(str(e))
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        raise InternalServerError("Failed to create user")

@bp.route('/<user_id>', methods=['GET'])
def get_user(user_id):
    try:
        user = mongo_service.get_user(user_id)
        user['_id'] = str(user['_id'])  # Convertir ObjectId a string
        return jsonify(user), 200
    except ValueError as e:
        raise NotFound(str(e))
    except Exception as e:
        logger.error(f"Error getting user: {str(e)}")
        raise InternalServerError("Failed to get user")

@bp.route('/<user_id>', methods=['PUT'])
def update_user(user_id):
    try:
        data = request.get_json()
        update_data = UserUpdate(**data).dict(exclude_unset=True)
        
        if 'password' in update_data:
            # En producción, aquí deberías hashear la nueva contraseña
            pass
        
        mongo_service.update_user(user_id, update_data)
        return jsonify({"message": "User updated successfully"}), 200
    except ValueError as e:
        raise BadRequest(str(e))
    except Exception as e:
        logger.error(f"Error updating user: {str(e)}")
        raise InternalServerError("Failed to update user")

@bp.route('/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        mongo_service.delete_user(user_id)
        return jsonify({"message": "User deleted successfully"}), 200
    except ValueError as e:
        raise NotFound(str(e))
    except Exception as e:
        logger.error(f"Error deleting user: {str(e)}")
        raise InternalServerError("Failed to delete user")

@bp.route('/', methods=['GET'])
def list_users():
    try:
        skip = int(request.args.get('skip', 0))
        limit = int(request.args.get('limit', 10))
        
        users = mongo_service.list_users(skip, limit)
        for user in users:
            user['_id'] = str(user['_id'])  # Convertir ObjectId a string
        
        return jsonify(users), 200
    except Exception as e:
        logger.error(f"Error listing users: {str(e)}")
        raise InternalServerError("Failed to list users")

@bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200