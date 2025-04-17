from app.services.mongo_service import save_event_to_mongo
from app.services.kafka_service import KafkaService
from app.config import Config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def handle_user_registration(event):
    try:
        # Guardar evento en MongoDB
        save_event_to_mongo(event)
        logger.info(f"User registration event saved: {event}")
    except Exception as e:
        logger.error(f"Error handling user registration: {e}")

def handle_welcome_event(event):
    try:
        # Guardar evento en MongoDB
        save_event_to_mongo(event)
        logger.info(f"Welcome event saved: {event}")
        
        # Aquí podrías agregar lógica adicional para enviar el email
        # Por ahora solo lo registramos
    except Exception as e:
        logger.error(f"Error handling welcome event: {e}")

def start_event_consumers():
    # Iniciar consumidores en segundo plano
    from threading import Thread

    # Consumidor para eventos de registro
    Thread(target=lambda: KafkaService.consume_events(
        Config.USER_TOPIC,
        'user-service-group',
        handle_user_registration
    )).start()

    # Consumidor para eventos de bienvenida
    Thread(target=lambda: KafkaService.consume_events(
        Config.WELCOME_TOPIC,
        'welcome-service-group',
        handle_welcome_event
    )).start()