import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Kafka
    KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
    USER_REGISTRATION_TOPIC = os.getenv("USER_REGISTRATION_TOPIC", "user-registration")
    
    # MongoDB
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongodb:27017/")
    MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "ecommerce_events")
    MONGO_USER_COLLECTION = os.getenv("MONGO_USER_COLLECTION", "users")
    
    # Application
    SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")