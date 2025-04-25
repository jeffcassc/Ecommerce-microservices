from datetime import datetime
from bson import ObjectId
from app import mongo

class Notification:
    @staticmethod
    def create(notification_data):
        notification_data['created_at'] = datetime.utcnow()
        result = mongo.db.notifications.insert_one(notification_data)
        return str(result.inserted_id)

    @staticmethod
    def get_by_id(notification_id):
        return mongo.db.notifications.find_one({'_id': ObjectId(notification_id)})

    @staticmethod
    def get_by_recipient(recipient):
        return list(mongo.db.notifications.find({'recipient': recipient}))

    @staticmethod
    def get_all():
        return list(mongo.db.notifications.find())

    @staticmethod
    def get_by_type(notification_type):
        return list(mongo.db.notifications.find({'type': notification_type}))