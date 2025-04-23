from app.models import Product
from app.schemas import ProductSchema, ProductUpdateSchema
from app.services.kafka_service import KafkaService
from app.services.mongo_service import save_event_to_mongo
from app.config import Config
from bson import ObjectId
from datetime import datetime
import logging
import uuid

logger = logging.getLogger(__name__)

class ProductService:
    @staticmethod
    def create_product(product_data):
        # Validar datos
        schema = ProductSchema()
        errors = schema.validate(product_data)
        if errors:
            raise ValueError(errors)

        # Verificar si el producto ya existe
        if Product.get_by_name(product_data['name']):
            raise ValueError("Product with this name already exists")

        # Crear producto
        product_id = Product.create(product_data)
        product = Product.get_by_id(product_id)

        # Publicar evento
        KafkaService.produce_event(
            topic=Config.PRODUCT_TOPIC,
            source="ProductService",
            payload=product_data,
            snapshot={
                "productId": str(product['_id']),
                "status": "CREATED",
                "timestamp": datetime.utcnow().isoformat()
            }
        )

        return product

    @staticmethod
    def get_product(product_id):
        try:
            if not ObjectId.is_valid(product_id):
                raise ValueError("Invalid product ID format")
            product_obj_id = ObjectId(product_id)
        except Exception:
            raise ValueError("Invalid product ID format")
        product = Product.get_by_id(product_obj_id)
        if not product:
            raise ValueError("Product not found")
        return product

    @staticmethod
    def get_all_products():
        products = Product.get_all()
        return products

    @staticmethod
    def update_product(product_id, update_data):
        try:
            if not ObjectId.is_valid(product_id):
                raise ValueError("Invalid product ID format")
            product_obj_id = ObjectId(product_id)
        except Exception:
            raise ValueError("Invalid product ID format")
            
        schema = ProductUpdateSchema()
        errors = schema.validate(update_data)
        if errors:
            raise ValueError(errors)

        result = Product.update(product_obj_id, update_data)
        if result.modified_count == 0:
            raise ValueError("Product not found or no changes made")

        product = Product.get_by_id(product_obj_id)
        
        # Publicar evento de actualización
        KafkaService.produce_event(
            topic=Config.PRODUCT_TOPIC,
            source="ProductService",
            payload=update_data,
            snapshot={
                "productId": str(product['_id']),
                "status": "UPDATED",
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        return product

    @staticmethod
    def delete_product(product_id):
        try:
            if not ObjectId.is_valid(product_id):
                raise ValueError("Invalid product ID format")
            product_obj_id = ObjectId(product_id)
        except Exception:
            raise ValueError("Invalid product ID format")
            
        product = Product.get_by_id(product_obj_id)
        if not product:
            raise ValueError("Product not found")

        result = Product.delete(product_obj_id)
        if result.deleted_count == 0:
            raise ValueError("Product not found")

        # Publicar evento de eliminación
        KafkaService.produce_event(
            topic=Config.PRODUCT_TOPIC,
            source="ProductService",
            payload={"productId": str(product['_id'])},
            snapshot={
                "productId": str(product['_id']),
                "status": "DELETED",
                "timestamp": datetime.utcnow().isoformat()
            }
        )

        return {"message": "Product deleted successfully"}

    @staticmethod
    def get_products_by_category(category):
        products = Product.get_by_category(category)
        return products

    @staticmethod
    def search_products(query):
        products = Product.search(query)
        return products