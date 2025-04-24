from app import mongo
from datetime import datetime
from bson import json_util
import json
import logging

logger = logging.getLogger(__name__)

def save_event_to_mongo(event):
    """
    Save event to MongoDB with robust data type handling
    """
    try:
        event_to_store = event.copy()
        
        if 'timestamp' in event_to_store and isinstance(event_to_store['timestamp'], datetime):
            event_to_store['timestamp'] = event_to_store['timestamp'].isoformat()
        
        event_to_store['stored_at'] = datetime.utcnow()
        event_to_store = json.loads(json_util.dumps(event_to_store))
        
        result = mongo.db.events.insert_one(event_to_store)
        logger.info(f"Event saved to MongoDB with ID: {result.inserted_id}")
        return result.inserted_id
        
    except Exception as e:
        logger.error(f"Failed to save event to MongoDB. Error: {str(e)}", exc_info=True)
        raise