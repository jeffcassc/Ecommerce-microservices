import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'localhost:9092')
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/ecommerce')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    CART_UPDATES_TOPIC = 'cart-updates'
    CART_REMOVALS_TOPIC = 'cart-removals'
    NOTIFICATION_TOPIC = 'notification-topic'