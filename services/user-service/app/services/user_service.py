from app.models import User
from app.schemas import UserSchema, UserUpdateSchema, LoginSchema
from app.services.kafka_service import KafkaService
from app.services.mongo_service import save_event_to_mongo
from app.config import Config
from bson import ObjectId
import hashlib
import uuid
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class UserService:
    @staticmethod
    def register_user(user_data):
        # Validar datos
        schema = UserSchema()
        errors = schema.validate(user_data)
        if errors:
            raise ValueError(errors)

        # Verificar si el usuario ya existe
        if User.get_by_email(user_data['email']):
            raise ValueError("User already exists")

        # Hash de la contraseña
        user_data['password'] = hashlib.sha256(user_data['password'].encode()).hexdigest()
        user_data['user_id'] = str(uuid.uuid4())

        # Crear usuario
        user_id = User.create(user_data)
        user = User.get_by_id(user_id)

        # Publicar eventos (manejar serialización de fechas)
        user_data_for_event = user_data.copy()
        user_data_for_event.pop('password', None)  # No enviar contraseña en el evento
        
        KafkaService.produce_event(
            topic=Config.USER_TOPIC,
            source="UserService",
            payload=user_data_for_event,
            snapshot={
                "userId": user['user_id'],
                "status": "REGISTERED",
                "timestamp": datetime.utcnow().isoformat()
            }
        )

        welcome_payload = {
            "to": user['email'],
            "subject": "¡Bienvenido!",
            "content": f"Hola {user['name']}, gracias por registrarte."
        }

        KafkaService.produce_event(
            topic=Config.USER_TOPIC,
            source="UserService",
            payload={
                **user_data_for_event,
                "registration_timestamp": datetime.utcnow().isoformat()
            },
            snapshot={
                "userId": user['user_id'],
                "status": "REGISTERED",
                "timestamp": datetime.utcnow().isoformat()
            }
        )

        return user

    @staticmethod
    def get_user(user_id):
        try:
            if not ObjectId.is_valid(user_id):
                raise ValueError("Invalid user ID format")
            user_obj_id = ObjectId(user_id)
        except Exception:
            raise ValueError("Invalid user ID format")
        user = User.get_by_id(user_obj_id)
        if not user:
            raise ValueError("User not found")
        return user

    @staticmethod
    def get_all_users():
        users = User.get_all()
        return users

    @staticmethod
    def update_user(user_id, update_data):
        try:
            if not ObjectId.is_valid(user_id):
                raise ValueError("Invalid user ID format")
            user_obj_id = ObjectId(user_id)
        except Exception:
            raise ValueError("Invalid user ID format")
            
        schema = UserUpdateSchema()
        errors = schema.validate(update_data)
        if errors:
            raise ValueError(errors)

        if 'email' in update_data:
            existing_user = User.get_by_email(update_data['email'])
            if existing_user and str(existing_user['_id']) != user_id:
                raise ValueError("Email already in use")

        result = User.update(user_obj_id, update_data)
        if result.modified_count == 0:
            raise ValueError("User not found or no changes made")

        user = User.get_by_id(user_obj_id)
        
        # Publicar evento de actualización
        KafkaService.produce_event(
            topic="user-updates",
            source="UserService",
            payload={
                **update_data,
                "update_timestamp": datetime.utcnow().isoformat()  # Fecha como string
            },
            snapshot={
                "userId": user['user_id'],
                "status": "UPDATED",
                "timestamp": datetime.utcnow().isoformat()  # Fecha como string
            }
        )
        return user

    @staticmethod
    def delete_user(user_id):
        try:
            if not ObjectId.is_valid(user_id):
                raise ValueError("Invalid user ID format")
            user_obj_id = ObjectId(user_id)
        except Exception:
            raise ValueError("Invalid user ID format")
            
        user = User.get_by_id(user_obj_id)
        if not user:
            raise ValueError("User not found")

        result = User.delete(user_obj_id)
        if result.deleted_count == 0:
            raise ValueError("User not found")

        # Publicar evento de eliminación
        KafkaService.produce_event(
            topic="user-deletions",
            source="UserService",
            payload={"userId": user['user_id']},
            snapshot={
                "userId": user['user_id'],
                "status": "DELETED",
                "timestamp": datetime.utcnow().isoformat()
            }
        )

        return {"message": "User deleted successfully"}

    @staticmethod
    def login_user(login_data):
        schema = LoginSchema()
        errors = schema.validate(login_data)
        if errors:
            raise ValueError(errors)

        user = User.get_by_email(login_data['email'])
        if not user:
            raise ValueError("Invalid credentials")

        hashed_password = hashlib.sha256(login_data['password'].encode()).hexdigest()
        if user['password'] != hashed_password:
            raise ValueError("Invalid credentials")

        # Publicar evento de login
        KafkaService.produce_event(
            topic="user-logins",
            source="UserService",
            payload={"email": login_data['email']},
            snapshot={
                "userId": user['user_id'],
                "status": "LOGGED_IN",
                "timestamp": datetime.utcnow().isoformat()
            }
        )

        return {"message": "Login successful", "user_id": user['user_id']}

# Handlers de eventos (deben estar al final para evitar importaciones circulares)
def handle_user_registration(event):
    try:
        save_event_to_mongo(event)
        logger.info(f"User registration event saved: {event}")
    except Exception as e:
        logger.error(f"Error handling user registration: {e}")

def handle_welcome_event(event):
    try:
        save_event_to_mongo(event)
        logger.info(f"Welcome event saved: {event}")
    except Exception as e:
        logger.error(f"Error handling welcome event: {e}")