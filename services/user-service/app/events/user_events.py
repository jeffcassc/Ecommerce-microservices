from app.services.mongo_service import save_event_to_mongo
from shared.kafka_service import KafkaService
from shared.kafka_config import KafkaConfig
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def handle_user_registration(event):
    try:
        # Save event to MongoDB
        save_event_to_mongo(event)
        logger.info(f"User registration event saved: {event}")
        
        # Extract user data from payload
        user_data = event.get('payload', {})
        email = user_data.get('email')
        name = user_data.get('name')
        
        if not email or not name:
            logger.error("Missing required fields in user registration event")
            return
            
        # Prepare welcome message
        welcome_payload = {
            "to": email,
            "subject": "¡Bienvenido a nuestra plataforma!",
            "content": f"Hola {name}, gracias por registrarte en nuestro e-commerce."
        }
        
        # Send welcome event to notification service
        KafkaService.produce_event(
            topic=KafkaConfig.WELCOME_TOPIC,
            source="UserService",
            payload=welcome_payload,
            snapshot={
                "userId": event.get('snapshot', {}).get('userId'),
                "status": "WELCOME_SENT",
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
    except Exception as e:
        logger.error(f"Error handling user registration: {e}")

def handle_welcome_event(event):
    try:
        # Save event to MongoDB
        save_event_to_mongo(event)
        logger.info(f"Welcome event saved: {event}")
        
        # Here you could add additional processing logic
        # For example, update user status or send metrics
        
    except Exception as e:
        logger.error(f"Error handling welcome event: {e}")