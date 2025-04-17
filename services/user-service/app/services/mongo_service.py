from app.config import Config
from flask_pymongo import PyMongo
from datetime import datetime

mongo = PyMongo()

def save_event_to_mongo(event):
    event_db = mongo.db.events
    event['created_at'] = datetime.utcnow()
    event_db.insert_one(event)
    return event