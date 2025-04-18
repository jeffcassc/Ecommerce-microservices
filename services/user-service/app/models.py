from datetime import datetime
from bson import ObjectId
from flask_pymongo import PyMongo
from app import mongo  # Importamos mongo desde app

class User:
    @staticmethod
    def create(user_data):
        user_data['created_at'] = datetime.utcnow()
        user_data['updated_at'] = datetime.utcnow()
        result = mongo.db.users.insert_one(user_data)
        return str(result.inserted_id)

    @staticmethod
    def get_by_id(user_id):
        return mongo.db.users.find_one({'_id': ObjectId(user_id)})

    @staticmethod
    def get_by_email(email):
        return mongo.db.users.find_one({'email': email})

    @staticmethod
    def update(user_id, update_data):
        update_data['updated_at'] = datetime.utcnow()
        return mongo.db.users.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': update_data}
        )

    @staticmethod
    def delete(user_id):
        return mongo.db.users.delete_one({'_id': ObjectId(user_id)})

    @staticmethod
    def get_all():
        return list(mongo.db.users.find())