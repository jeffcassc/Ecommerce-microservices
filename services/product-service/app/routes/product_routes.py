from flask import Blueprint, request, jsonify
from app.services.product_service import ProductService
from bson import ObjectId
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

product_bp = Blueprint('product', __name__, url_prefix='/api/products')

@product_bp.route('/', methods=['POST'])
def create_product():
    try:
        # Verificar que el contenido es JSON
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400
            
        data = request.get_json(force=True)  # force=True para manejar mejor los errores
        
        logger.info(f"Received product data: {data}")
        
        # Validar campos mínimos
        required_fields = ['name', 'description', 'price', 'category', 'stock']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400
            
        product = ProductService.create_product(data)
        return jsonify({
            "message": "Product created successfully",
            "product_id": str(product['_id'])
        }), 201
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Unexpected error in product creation: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500

@product_bp.route('/<product_id>', methods=['GET'])
def get_product(product_id):
    try:
        product = ProductService.get_product(product_id)
        product['_id'] = str(product['_id'])  # Convert ObjectId to string
        return jsonify(product), 200
    except ValueError as e:
        logger.error(f"Error getting product: {str(e)}")
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        logger.error(f"Unexpected error getting product: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500

@product_bp.route('/', methods=['GET'])
def get_all_products():
    try:
        products = ProductService.get_all_products()
        for product in products:
            product['_id'] = str(product['_id'])  # Convert ObjectId to string
        return jsonify(products), 200
    except Exception as e:
        logger.error(f"Error getting all products: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500

@product_bp.route('/<product_id>', methods=['PUT'])
def update_product(product_id):
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        product = ProductService.update_product(product_id, data)
        product['_id'] = str(product['_id'])  # Convert ObjectId to string
        return jsonify({
            "message": "Product updated successfully",
            "product": product
        }), 200
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Error updating product: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500

@product_bp.route('/<product_id>', methods=['DELETE'])
def delete_product(product_id):
    try:
        result = ProductService.delete_product(product_id)
        return jsonify(result), 200
    except ValueError as e:
        logger.error(f"Error deleting product: {str(e)}")
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        logger.error(f"Error deleting product: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500

@product_bp.route('/category/<category>', methods=['GET'])
def get_products_by_category(category):
    try:
        products = ProductService.get_products_by_category(category)
        for product in products:
            product['_id'] = str(product['_id'])  # Convert ObjectId to string
        return jsonify(products), 200
    except Exception as e:
        logger.error(f"Error getting products by category: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500

@product_bp.route('/search', methods=['GET'])
def search_products():
    try:
        query = request.args.get('q')
        if not query:
            return jsonify({"error": "Query parameter 'q' is required"}), 400
            
        products = ProductService.search_products(query)
        for product in products:
            product['_id'] = str(product['_id'])  # Convert ObjectId to string
        return jsonify(products), 200
    except Exception as e:
        logger.error(f"Error searching products: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500