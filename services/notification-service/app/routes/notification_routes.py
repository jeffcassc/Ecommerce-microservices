from flask import Blueprint, request, jsonify
from app.services.notification_service import NotificationService
import logging
from bson import json_util
import json

logger = logging.getLogger(__name__)

notification_bp = Blueprint('notification', __name__, url_prefix='/api/notifications')

@notification_bp.route('/', methods=['GET'])
def get_notifications():
    try:
        from app import mongo
        notifications = list(mongo.db.events.find({"source": "NotificationService"}))
        return jsonify(json.loads(json_util.dumps(notifications))), 200
    except Exception as e:
        logger.error(f"Error getting notifications: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500

@notification_bp.route('/test/welcome', methods=['POST'])
def test_welcome_notification():
    try:
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400
            
        data = request.get_json(force=True)
        logger.info(f"Received test welcome notification data: {data}")
        
        test_event = {
            "payload": {
                "to": data.get('email'),
                "subject": "Test Welcome Email",
                "content": "This is a test welcome email"
            }
        }
        
        result = NotificationService.send_welcome_notification(test_event)
        return jsonify({
            "message": "Test welcome notification sent",
            "notification": json.loads(json_util.dumps(result))
        }), 200
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Unexpected error sending test welcome notification: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500