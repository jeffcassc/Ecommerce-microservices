from datetime import datetime
from bson import ObjectId
from app import mongo

class Product:
    @staticmethod
    def create(product_data):
        product_data['created_at'] = datetime.utcnow()
        product_data['updated_at'] = datetime.utcnow()
        result = mongo.db.products.insert_one(product_data)
        return str(result.inserted_id)

    @staticmethod
    def get_by_id(product_id):
        return mongo.db.products.find_one({'_id': ObjectId(product_id)})

    @staticmethod
    def get_by_name(name):
        return mongo.db.products.find_one({'name': name})

    @staticmethod
    def update(product_id, update_data):
        update_data['updated_at'] = datetime.utcnow()
        return mongo.db.products.update_one(
            {'_id': ObjectId(product_id)},
            {'$set': update_data}
        )

    @staticmethod
    def delete(product_id):
        return mongo.db.products.delete_one({'_id': ObjectId(product_id)})

    @staticmethod
    def get_all():
        return list(mongo.db.products.find())

    @staticmethod
    def get_by_category(category):
        return list(mongo.db.products.find({'category': category}))

    @staticmethod
    def search(query):
        return list(mongo.db.products.find({
            '$or': [
                {'name': {'$regex': query, '$options': 'i'}},
                {'description': {'$regex': query, '$options': 'i'}},
                {'category': {'$regex': query, '$options': 'i'}}
            ]
        }))