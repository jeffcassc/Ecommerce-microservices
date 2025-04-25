from app.services.notification_service import NotificationService
from app.services.mongo_service import save_event_to_mongo
from shared.kafka_config import KafkaConfig
import logging
from datetime import datetime

from shared.kafka_service import KafkaService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def handle_welcome_notification(event):
    try:
        logger.info(f"Processing welcome notification event: {event['eventId']}")
        
        # 1. Save the received event to MongoDB
        save_event_to_mongo({
            **event,
            "processing_started_at": datetime.utcnow()
        })
        
        # 2. Process the notification
        notification_result = NotificationService.send_welcome_notification(event)
        
        logger.info(f"Welcome notification processed successfully for event {event['eventId']}")
        return notification_result
        
    except Exception as e:
        logger.error(f"Error handling welcome notification event {event.get('eventId', 'unknown')}: {str(e)}", exc_info=True)
        raise

def handle_cart_removal_notification(event):
    try:
        logger.info(f"Processing cart removal notification event: {event['eventId']}")
        
        # Validate minimum payload
        if not event.get('payload') or not event['payload'].get('to'):
            raise ValueError("Invalid payload: missing recipient email")
        
        # 1. Save the received event
        save_event_to_mongo({
            **event,
            "processing_started_at": datetime.utcnow()
        })
        
        # 2. Process the notification
        notification_result = NotificationService.send_cart_removal_notification(event)
        
        logger.info(f"Cart removal notification processed for event {event['eventId']}")
        return notification_result
        
    except Exception as e:
        logger.error(f"Error handling cart removal event {event.get('eventId', 'unknown')}: {str(e)}", exc_info=True)
        raise

def handle_order_notification(event):
    try:
        logger.info(f"Processing order notification event: {event['eventId']}")
        
        # Validate event structure
        if not event.get('snapshot') or not event['snapshot'].get('orderId'):
            raise ValueError("Invalid order notification: missing order ID")
        
        # 1. Save the original event
        save_event_to_mongo({
            **event,
            "processing_started_at": datetime.utcnow()
        })
        
        # 2. Process the notification
        notification_result = NotificationService.send_order_notification(event)
        
        logger.info(f"Order notification processed for order {event['snapshot']['orderId']}")
        return notification_result
        
    except Exception as e:
        logger.error(f"Error handling order notification {event.get('eventId', 'unknown')}: {str(e)}", exc_info=True)
        raise

def start_event_consumers():
    """
    Start all event consumers in separate threads
    """
    from threading import Thread
    
    consumers = [
        {
            "topic": KafkaConfig.WELCOME_TOPIC,
            "handler": handle_welcome_notification,
            "group_id": "notification-welcome-group"
        },
        {
            "topic": KafkaConfig.CART_REMOVALS_TOPIC,
            "handler": handle_cart_removal_notification,
            "group_id": "notification-cart-group"
        },
        {
            "topic": KafkaConfig.INVOICE_PROCESSING_TOPIC,
            "handler": handle_order_notification,
            "group_id": "notification-order-group"
        }
    ]
    
    for consumer in consumers:
        Thread(
            target=lambda c: KafkaService.consume_events(
                c['topic'],
                c['group_id'],
                c['handler']
            ),
            args=(consumer,),
            daemon=True
        ).start()
    
    logger.info("Started all notification event consumers")