from flask import Blueprint, request, jsonify
from app.services.cart_service import CartService
import logging
from bson import json_util
import json

logger = logging.getLogger(__name__)

cart_bp = Blueprint('cart', __name__, url_prefix='/api/cart')

@cart_bp.route('/items', methods=['POST'])
def add_item():
    try:
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400
            
        data = request.get_json(force=True)
        logger.info(f"Received cart item data: {data}")
        
        cart = CartService.add_item_to_cart(data)
        return jsonify({
            "message": "Item added to cart",
            "cart": json.loads(json_util.dumps(cart))
        }), 200
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Unexpected error adding item to cart: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500

@cart_bp.route('/items/<product_id>', methods=['DELETE'])
def remove_item(product_id):
    try:
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400
            
        data = request.get_json(force=True)
        data['productId'] = product_id
        
        cart = CartService.remove_item_from_cart(data)
        return jsonify({
            "message": "Item removed from cart",
            "cart": json.loads(json_util.dumps(cart))
        }), 200
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Unexpected error removing item from cart: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500

@cart_bp.route('/', methods=['GET'])
def get_cart():
    try:
        user_id = request.args.get('userId')
        if not user_id:
            return jsonify({"error": "userId parameter is required"}), 400
            
        cart = CartService.get_cart(user_id)
        return jsonify(json.loads(json_util.dumps(cart))), 200
    except ValueError as e:
        logger.error(f"Error getting cart: {str(e)}")
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        logger.error(f"Unexpected error getting cart: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500

@cart_bp.route('/', methods=['DELETE'])
def clear_cart():
    try:
        user_id = request.args.get('userId')
        if not user_id:
            return jsonify({"error": "userId parameter is required"}), 400
            
        result = CartService.clear_cart(user_id)
        return jsonify(result), 200
    except ValueError as e:
        logger.error(f"Error clearing cart: {str(e)}")
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        logger.error(f"Unexpected error clearing cart: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500