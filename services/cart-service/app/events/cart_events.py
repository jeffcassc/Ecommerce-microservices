from app.services.mongo_service import save_event_to_mongo
from app.services.kafka_service import KafkaService
from app.config import Config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def handle_cart_updated(event):
    try:
        save_event_to_mongo(event)
        logger.info(f"Cart updated event saved: {event}")
        
        # Here you could add additional processing logic
        # For example, update inventory or send notifications
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
                topic=Config.NOTIFICATION_TOPIC,
                source="CartService",
                payload=notification_payload,
                snapshot=event['snapshot']
            )
    except Exception as e:
        logger.error(f"Error handling cart item removed event: {e}")

def start_event_consumers():
    from threading import Thread

    Thread(target=lambda: KafkaService.consume_events(
        Config.CART_UPDATES_TOPIC,
        'cart-service-group',
        handle_cart_updated
    )).start()

    Thread(target=lambda: KafkaService.consume_events(
        Config.CART_REMOVALS_TOPIC,
        'cart-service-group',
        handle_cart_item_removed
    )).start()