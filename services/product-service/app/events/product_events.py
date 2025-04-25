from app.services.mongo_service import save_event_to_mongo
from shared.kafka_service import KafkaService
from shared.kafka_config import KafkaConfig
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def handle_product_created(event):
    try:
        # Save event to MongoDB
        save_event_to_mongo(event)
        logger.info(f"Product created event saved: {event}")
        
        # Here you could add additional processing logic
        # For example, update search indexes, etc.
    except Exception as e:
        logger.error(f"Error handling product created event: {e}")

def handle_product_updated(event):
    try:
        # Save event to MongoDB
        save_event_to_mongo(event)
        logger.info(f"Product updated event saved: {event}")
    except Exception as e:
        logger.error(f"Error handling product updated event: {e}")

def handle_product_deleted(event):
    try:
        # Save event to MongoDB
        save_event_to_mongo(event)
        logger.info(f"Product deleted event saved: {event}")
    except Exception as e:
        logger.error(f"Error handling product deleted event: {e}")

def start_event_consumers():
    # Start background consumers
    from threading import Thread

    # Consumer for product events
    Thread(target=lambda: KafkaService.consume_events(
        KafkaConfig.PRODUCT_EVENTS_TOPIC,
        'product-service-group',
        handle_product_created
    )).start()