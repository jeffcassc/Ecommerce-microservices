from datetime import datetime
from bson import ObjectId
from app import mongo

class Cart:
    @staticmethod
    def get_or_create_cart(user_id):
        cart = mongo.db.carts.find_one({'userId': user_id})
        if not cart:
            cart_data = {
                'userId': user_id,
                'items': [],
                'createdAt': datetime.utcnow(),
                'updatedAt': datetime.utcnow()
            }
            result = mongo.db.carts.insert_one(cart_data)
            cart = mongo.db.carts.find_one({'_id': result.inserted_id})
        return cart

    @staticmethod
    def add_item(user_id, product_id, quantity):
        cart = Cart.get_or_create_cart(user_id)
        
        # Check if product already exists in cart
        item_index = next((i for i, item in enumerate(cart['items']) 
                          if item['productId'] == product_id), None)
        
        if item_index is not None:
            # Update quantity if product exists
            cart['items'][item_index]['quantity'] += quantity
        else:
            # Add new item
            cart['items'].append({
                'productId': product_id,
                'quantity': quantity,
                'addedAt': datetime.utcnow()
            })
        
        cart['updatedAt'] = datetime.utcnow()
        mongo.db.carts.update_one(
            {'_id': cart['_id']},
            {'$set': {
                'items': cart['items'],
                'updatedAt': cart['updatedAt']
            }}
        )
        return cart

    @staticmethod
    def remove_item(user_id, product_id):
        cart = Cart.get_or_create_cart(user_id)
        initial_count = len(cart['items'])
        
        cart['items'] = [item for item in cart['items'] 
                        if item['productId'] != product_id]
        
        if len(cart['items']) < initial_count:
            cart['updatedAt'] = datetime.utcnow()
            mongo.db.carts.update_one(
                {'_id': cart['_id']},
                {'$set': {
                    'items': cart['items'],
                    'updatedAt': cart['updatedAt']
                }}
            )
            return True
        return False

    @staticmethod
    def get_cart(user_id):
        return mongo.db.carts.find_one({'userId': user_id})

    @staticmethod
    def clear_cart(user_id):
        result = mongo.db.carts.update_one(
            {'userId': user_id},
            {'$set': {
                'items': [],
                'updatedAt': datetime.utcnow()
            }}
        )
        return result.modified_count > 0