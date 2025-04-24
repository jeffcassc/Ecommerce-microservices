from app.models import Cart
from app.schemas import AddCartItemSchema, RemoveCartItemSchema
from app.services.kafka_service import KafkaService
from app.services.mongo_service import save_event_to_mongo
from app.config import Config
from datetime import datetime
import logging
import uuid

logger = logging.getLogger(__name__)

class CartService:
    @staticmethod
    def add_item_to_cart(cart_data):
        # Validate data
        schema = AddCartItemSchema()
        errors = schema.validate(cart_data)
        if errors:
            raise ValueError(errors)

        # Add item to cart
        cart = Cart.add_item(
            cart_data['userId'],
            cart_data['productId'],
            cart_data['quantity']
        )

        # Publish event
        KafkaService.produce_event(
            topic=Config.CART_UPDATES_TOPIC,
            source="CartService",
            payload=cart_data,
            snapshot={
                "cartId": str(cart['_id']),
                "userId": cart['userId'],
                "totalItems": len(cart['items']),
                "updatedAt": datetime.utcnow().isoformat()
            }
        )

        return cart

    @staticmethod
    def remove_item_from_cart(remove_data):
        # Validate data
        schema = RemoveCartItemSchema()
        errors = schema.validate(remove_data)
        if errors:
            raise ValueError(errors)

        # Remove item from cart
        removed = Cart.remove_item(
            remove_data['userId'],
            remove_data.get('productId')
        )

        if not removed:
            raise ValueError("Item not found in cart")

        cart = Cart.get_cart(remove_data['userId'])

        # Publish event
        KafkaService.produce_event(
            topic=Config.CART_REMOVALS_TOPIC,
            source="CartService",
            payload=remove_data,
            snapshot={
                "cartId": str(cart['_id']),
                "userId": cart['userId'],
                "totalItems": len(cart['items']),
                "updatedAt": datetime.utcnow().isoformat()
            }
        )

        return cart

    @staticmethod
    def get_cart(user_id):
        cart = Cart.get_cart(user_id)
        if not cart:
            raise ValueError("Cart not found")
        return cart

    @staticmethod
    def clear_cart(user_id):
        cleared = Cart.clear_cart(user_id)
        if not cleared:
            raise ValueError("Cart not found or already empty")
        return {"message": "Cart cleared successfully"}