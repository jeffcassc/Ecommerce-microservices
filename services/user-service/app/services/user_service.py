import uuid
from datetime import datetime
import logging
from werkzeug.security import generate_password_hash
from app.models.user_models import UserCreate, UserInDB
from app.models.event_models import UserRegistrationEvent, WelcomeEvent
from app.services.kafka_service import kafka_producer
from app.services.mongo_service import mongo_service
from app.config import Config
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

class UserService:
    @staticmethod
    def generate_user_id() -> str:
        return f"usr_{uuid.uuid4().hex[:8]}"
    
    @staticmethod
    def hash_password(password: str) -> str:
        return generate_password_hash(
            password,
            method=Config.PASSWORD_HASH_METHOD.split(':')[1],
            salt_length=Config.PASSWORD_SALT_LENGTH
        )
    
    @staticmethod
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def register_user(user_data: UserCreate) -> UserInDB:
        try:
            # Verificar si el usuario ya existe
            existing_user = mongo_service.get_user_by_email(user_data.email)
            if existing_user:
                logger.warning(f"User with email {user_data.email} already exists")
                raise ValueError("User with this email already exists")
            
            # Crear usuario en la base de datos
            user_id = UserService.generate_user_id()
            current_time = datetime.utcnow()
            hashed_password = UserService.hash_password(user_data.password)
            
            user_dict = {
                "_id": user_id,
                "name": user_data.name,
                "last_name": user_data.last_name,
                "email": user_data.email,
                "phone": user_data.phone,
                "created_at": current_time,
                "updated_at": current_time,
                "status": "REGISTERED",
                "hashed_password": hashed_password
            }
            
            # Guardar usuario en MongoDB
            mongo_service.insert_user(user_dict)
            
            # Crear y publicar eventos
            registration_event = UserRegistrationEvent(
                event_id=f"evt_{uuid.uuid4().hex}",
                timestamp=current_time,
                source="UserService",
                topic=Config.USER_REGISTRATION_TOPIC,
                payload=user_data.dict(exclude={"password"}),
                snapshot={
                    "userId": user_id,
                    "status": "REGISTERED",
                    "createdAt": current_time.isoformat()
                }
            ).dict()
            
            welcome_event = WelcomeEvent(
                event_id=f"evt_{uuid.uuid4().hex}",
                timestamp=current_time,
                source="UserService",
                topic=Config.WELCOME_FLOW_TOPIC,
                payload={
                    "to": user_data.email,
                    "subject": "¡Bienvenido a nuestra plataforma!",
                    "content": f"Hola {user_data.name}, gracias por registrarte en nuestro e-commerce."
                },
                snapshot={
                    "userId": user_id,
                    "emailSent": True,
                    "sentAt": current_time.isoformat()
                }
            ).dict()
            
            # Publicar eventos
            kafka_producer.publish_event(Config.USER_REGISTRATION_TOPIC, registration_event)
            kafka_producer.publish_event(Config.WELCOME_FLOW_TOPIC, welcome_event)
            
            # Guardar eventos en MongoDB
            mongo_service.insert_event(registration_event)
            mongo_service.insert_event(welcome_event)
            
            # Crear respuesta
            return UserInDB(**user_dict)
            
        except Exception as e:
            logger.error(f"Error in user registration: {str(e)}")
            raise