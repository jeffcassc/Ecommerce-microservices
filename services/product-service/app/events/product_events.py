from app.services.mongo_service import save_event_to_mongo
from app.services.kafka_service import KafkaService
from app.config import Config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def handle_product_created(event):
    try:
        # Guardar evento en MongoDB
        save_event_to_mongo(event)
        logger.info(f"Product created event saved: {event}")
        
        # Aquí podrías agregar lógica adicional para procesar el evento
        # Por ejemplo, actualizar índices de búsqueda, etc.
    except Exception as e:
        logger.error(f"Error handling product created event: {e}")

def handle_product_updated(event):
    try:
        # Guardar evento en MongoDB
        save_event_to_mongo(event)
        logger.info(f"Product updated event saved: {event}")
    except Exception as e:
        logger.error(f"Error handling product updated event: {e}")

def handle_product_deleted(event):
    try:
        # Guardar evento en MongoDB
        save_event_to_mongo(event)
        logger.info(f"Product deleted event saved: {event}")
    except Exception as e:
        logger.error(f"Error handling product deleted event: {e}")

def start_event_consumers():
    # Iniciar consumidores en segundo plano
    from threading import Thread

    # Consumidor para eventos de productos
    Thread(target=lambda: KafkaService.consume_events(
        Config.PRODUCT_TOPIC,
        'product-service-group',
        handle_product_created
    )).start()