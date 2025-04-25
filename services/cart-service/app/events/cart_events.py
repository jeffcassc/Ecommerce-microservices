from app.services.mongo_service import save_event_to_mongo
from shared.kafka_service import KafkaService
from shared.kafka_config import KafkaConfig
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def handle_cart_updated(event):
    try:
        save_event_to_mongo(event)
        logger.info(f"Cart updated event saved: {event}")
        
        # Here you could add additional processing logic
        # For example, update inventory or send metrics
        
    except Exception as e:
        logger.error(f"Error handling cart updated event: {e}")

def handle_cart_item_removed(event):
    try:
        save_event_to_mongo(event)
        logger.info(f"Cart item removed event saved: {event}")
        
        # Example: Send notification about removed item
        if 'payload' in event and 'productId' in event['payload']:
            notification_payload = {
                "to": "user@example.com",  # In a real app, get from user service
                "subject": "Item removed from cart",
                "content": f"Item {event['payload']['productId']} was removed from your cart"
            }
            
            KafkaService.produce_event(
                topic=KafkaConfig.NOTIFICATION_TOPIC,
                source="CartService",
                payload=notification_payload,
                snapshot=event['snapshot']
            )
    except Exception as e:
        logger.error(f"Error handling cart item removed event: {e}")