from app import mongo
from datetime import datetime
from bson import json_util
import json
import logging

# Configurar logger
logger = logging.getLogger(__name__)

def save_event_to_mongo(event):
    """
    Guarda un evento en MongoDB con manejo robusto de tipos de datos y errores
    """
    try:
        # Convertir el evento a un formato compatible con MongoDB
        event_to_store = event.copy()
        
        # Asegurar que las fechas estén en formato ISO string
        if 'timestamp' in event_to_store and isinstance(event_to_store['timestamp'], datetime):
            event_to_store['timestamp'] = event_to_store['timestamp'].isoformat()
        
        # Añadir marca de tiempo de almacenamiento
        event_to_store['stored_at'] = datetime.utcnow()
        
        # Convertir cualquier tipo especial (como ObjectId) a formato serializable
        event_to_store = json.loads(json_util.dumps(event_to_store))
        
        # Insertar en la colección de eventos
        result = mongo.db.events.insert_one(event_to_store)
        logger.info(f"Event saved to MongoDB with ID: {result.inserted_id}")
        return result.inserted_id
        
    except Exception as e:
        logger.error(f"Failed to save event to MongoDB. Error: {str(e)}", exc_info=True)
        raise