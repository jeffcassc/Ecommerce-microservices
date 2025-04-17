from flask import Blueprint, request, jsonify
from app.services.user_service import UserService
from bson import ObjectId
import json

user_bp = Blueprint('user', __name__, url_prefix='/api/users')

@user_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        user = UserService.register_user(data)
        return jsonify({
            "message": "User registered successfully",
            "user_id": str(user['_id']),
            "user_uuid": user['user_id']
        }), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500

@user_bp.route('/<user_id>', methods=['GET'])
def get_user(user_id):
    try:
        user = UserService.get_user(user_id)
        user['_id'] = str(user['_id'])  # Convert ObjectId to string
        return jsonify(user), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500

@user_bp.route('/', methods=['GET'])
def get_all_users():
    try:
        users = UserService.get_all_users()
        for user in users:
            user['_id'] = str(user['_id'])  # Convert ObjectId to string
        return jsonify(users), 200
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500

@user_bp.route('/<user_id>', methods=['PUT'])
def update_user(user_id):
    try:
        data = request.get_json()
        user = UserService.update_user(user_id, data)
        user['_id'] = str(user['_id'])  # Convert ObjectId to string
        return jsonify({
            "message": "User updated successfully",
            "user": user
        }), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500

@user_bp.route('/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        result = UserService.delete_user(user_id)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500

@user_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        result = UserService.login_user(data)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 401
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500