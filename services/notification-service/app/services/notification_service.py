import logging
from app.services.mongo_service import save_event_to_mongo
from datetime import datetime
from uuid import uuid4

logger = logging.getLogger(__name__)

class NotificationService:
    @staticmethod
    def send_welcome_notification(event):
        try:
            payload = event.get('payload', {})
            email = payload.get('to')
            subject = payload.get('subject')
            content = payload.get('content')
            
            if not all([email, subject, content]):
                raise ValueError("Missing required notification fields")
            
            # Simulate sending email
            logger.info(f"Sending welcome email to {email} with subject: {subject}")
            
            # Save notification event
            notification_event = {
                "eventId": str(uuid4()),
                "timestamp": datetime.utcnow(),
                "source": "NotificationService",
                "topic": "notification-sent",
                "payload": payload,
                "snapshot": {
                    "status": "SENT",
                    "recipient": email,
                    "notificationType": "WELCOME"
                }
            }
            
            save_event_to_mongo(notification_event)
            return notification_event
            
        except Exception as e:
            logger.error(f"Error sending welcome notification: {str(e)}")
            raise

    @staticmethod
    def send_cart_removal_notification(event):
        try:
            payload = event.get('payload', {})
            email = payload.get('to')
            subject = payload.get('subject')
            content = payload.get('content')
            
            if not all([email, subject, content]):
                raise ValueError("Missing required notification fields")
            
            # Simulate sending email
            logger.info(f"Sending cart removal email to {email} with subject: {subject}")
            
            # Save notification event
            notification_event = {
                "eventId": str(uuid4()),
                "timestamp": datetime.utcnow(),
                "source": "NotificationService",
                "topic": "notification-sent",
                "payload": payload,
                "snapshot": {
                    "status": "SENT",
                    "recipient": email,
                    "notificationType": "CART_REMOVAL"
                }
            }
            
            save_event_to_mongo(notification_event)
            return notification_event
            
        except Exception as e:
            logger.error(f"Error sending cart removal notification: {str(e)}")
            raise

    @staticmethod
    def send_order_notification(event):
        try:
            payload = event.get('payload', {})
            email = payload.get('to')
            subject = payload.get('subject')
            content = payload.get('content')
            
            if not all([email, subject, content]):
                raise ValueError("Missing required notification fields")
            
            # Simulate sending email
            logger.info(f"Sending order confirmation email to {email} with subject: {subject}")
            
            # Save notification event
            notification_event = {
                "eventId": str(uuid4()),
                "timestamp": datetime.utcnow(),
                "source": "NotificationService",
                "topic": "notification-sent",
                "payload": payload,
                "snapshot": {
                    "status": "SENT",
                    "recipient": email,
                    "notificationType": "ORDER_CONFIRMATION"
                }
            }
            
            save_event_to_mongo(notification_event)
            return notification_event
            
        except Exception as e:
            logger.error(f"Error sending order notification: {str(e)}")
            raise