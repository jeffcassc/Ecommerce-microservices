from app.models import User
from app.schemas import UserSchema, UserUpdateSchema, LoginSchema
from app.services.kafka_service import KafkaService
from app.services.mongo_service import save_event_to_mongo
from app.config import Config
from bson import ObjectId
import hashlib
import uuid

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

        # Hash de la contraseña (básico, en producción usar algo más seguro)
        user_data['password'] = hashlib.sha256(user_data['password'].encode()).hexdigest()
        user_data['user_id'] = str(uuid.uuid4())

        # Crear usuario
        user_id = User.create(user_data)
        user = User.get_by_id(user_id)

        # Publicar evento de registro
        KafkaService.produce_event(
            topic=Config.USER_TOPIC,
            source="UserService",
            payload=user_data,
            snapshot={
                "userId": user['user_id'],
                "status": "REGISTERED"
            }
        )

        # Publicar evento de bienvenida
        welcome_payload = {
            "to": user['email'],
            "subject": "¡Bienvenido a nuestra plataforma!",
            "content": f"Hola {user['name']}, gracias por registrarte en nuestro e-commerce."
        }

        KafkaService.produce_event(
            topic=Config.WELCOME_TOPIC,
            source="UserService",
            payload=welcome_payload
        )

        return user

    @staticmethod
    def get_user(user_id):
        user = User.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        return user

    @staticmethod
    def get_all_users():
        return User.get_all()

    @staticmethod
    def update_user(user_id, update_data):
        schema = UserUpdateSchema()
        errors = schema.validate(update_data)
        if errors:
            raise ValueError(errors)

        if 'email' in update_data:
            existing_user = User.get_by_email(update_data['email'])
            if existing_user and str(existing_user['_id']) != user_id:
                raise ValueError("Email already in use")

        result = User.update(user_id, update_data)
        if result.modified_count == 0:
            raise ValueError("User not found or no changes made")

        user = User.get_by_id(user_id)
        
        # Publicar evento de actualización
        KafkaService.produce_event(
            topic="user-updates",
            source="UserService",
            payload=update_data,
            snapshot={
                "userId": user['user_id'],
                "status": "UPDATED"
            }
        )

        return user

    @staticmethod
    def delete_user(user_id):
        user = User.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        result = User.delete(user_id)
        if result.deleted_count == 0:
            raise ValueError("User not found")

        # Publicar evento de eliminación
        KafkaService.produce_event(
            topic="user-deletions",
            source="UserService",
            payload={"userId": user['user_id']},
            snapshot={
                "userId": user['user_id'],
                "status": "DELETED"
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
                "status": "LOGGED_IN"
            }
        )

        return {"message": "Login successful", "user_id": user['user_id']}