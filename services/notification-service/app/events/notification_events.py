from app.services.notification_service import NotificationService
from app.services.mongo_service import save_event_to_mongo
from app.config import Config
import logging
from datetime import datetime

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def handle_welcome_notification(event):
    """
    Maneja eventos de notificaciones de bienvenida
    """
    try:
        logger.info(f"Processing welcome notification event: {event['eventId']}")
        
        # 1. Guardar el evento recibido en MongoDB
        save_event_to_mongo({
            **event,
            "processing_started_at": datetime.utcnow()
        })
        
        # 2. Procesar la notificación
        notification_result = NotificationService.send_welcome_notification(event)
        
        logger.info(f"Welcome notification processed successfully for event {event['eventId']}")
        return notification_result
        
    except Exception as e:
        logger.error(f"Error handling welcome notification event {event.get('eventId', 'unknown')}: {str(e)}", exc_info=True)
        raise

def handle_cart_removal_notification(event):
    """
    Maneja eventos de notificaciones por eliminación de carrito
    """
    try:
        logger.info(f"Processing cart removal notification event: {event['eventId']}")
        
        # Validar payload mínimo
        if not event.get('payload') or not event['payload'].get('to'):
            raise ValueError("Invalid payload: missing recipient email")
        
        # 1. Guardar el evento recibido
        save_event_to_mongo({
            **event,
            "processing_started_at": datetime.utcnow()
        })
        
        # 2. Procesar la notificación
        notification_result = NotificationService.send_cart_removal_notification(event)
        
        logger.info(f"Cart removal notification processed for event {event['eventId']}")
        return notification_result
        
    except Exception as e:
        logger.error(f"Error handling cart removal event {event.get('eventId', 'unknown')}: {str(e)}", exc_info=True)
        raise

def handle_order_notification(event):
    """
    Maneja eventos de notificaciones de pedidos
    """
    try:
        logger.info(f"Processing order notification event: {event['eventId']}")
        
        # Validar estructura del evento
        if not event.get('snapshot') or not event['snapshot'].get('orderId'):
            raise ValueError("Invalid order notification: missing order ID")
        
        # 1. Guardar el evento original
        save_event_to_mongo({
            **event,
            "processing_started_at": datetime.utcnow()
        })
        
        # 2. Procesar la notificación
        notification_result = NotificationService.send_order_notification(event)
        
        logger.info(f"Order notification processed for order {event['snapshot']['orderId']}")
        return notification_result
        
    except Exception as e:
        logger.error(f"Error handling order notification {event.get('eventId', 'unknown')}: {str(e)}", exc_info=True)
        raise

def handle_generic_notification(event):
    """
    Manejador genérico para cualquier notificación
    """
    try:
        logger.info(f"Processing generic notification event: {event['eventId']}")
        
        # Guardar evento con metadatos adicionales
        enhanced_event = {
            **event,
            "processing_started_at": datetime.utcnow(),
            "notification_type": "GENERIC"
        }
        save_event_to_mongo(enhanced_event)
        
        # Aquí podrías añadir lógica para diferentes tipos de notificaciones genéricas
        logger.info(f"Generic notification logged for event {event['eventId']}")
        
        return enhanced_event
        
    except Exception as e:
        logger.error(f"Error handling generic notification: {str(e)}", exc_info=True)
        raise

def start_event_consumers():
    """
    Inicia todos los consumidores de eventos en threads separados
    """
    from threading import Thread
    from app.services.kafka_service import KafkaService
    
    consumers = [
        {
            "topic": Config.WELCOME_TOPIC,
            "handler": handle_welcome_notification,
            "group_id": "notification-welcome-group"
        },
        {
            "topic": Config.CART_REMOVALS_TOPIC,
            "handler": handle_cart_removal_notification,
            "group_id": "notification-cart-group"
        },
        {
            "topic": Config.INVOICE_PROCESSING_TOPIC,
            "handler": handle_order_notification,
            "group_id": "notification-order-group"
        },
        {
            "topic": Config.NOTIFICATION_TOPIC,
            "handler": handle_generic_notification,
            "group_id": "notification-generic-group"
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