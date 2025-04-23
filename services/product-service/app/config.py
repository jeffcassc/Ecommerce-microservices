import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'localhost:9092')
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/ecommerce')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    PRODUCT_TOPIC = 'product-events'
    CATEGORY_TOPIC = 'category-events'
    INVENTORY_TOPIC = 'inventory-updates'