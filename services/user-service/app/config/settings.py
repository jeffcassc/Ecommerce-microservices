import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongodb:27017/")
    MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "ecommerce_events")
    USER_SERVICE_PORT = int(os.getenv("USER_SERVICE_PORT", 8000))
    
    # Configuración de Kafka Topics
    USER_REGISTRATION_TOPIC = "user-registration"
    WELCOME_FLOW_TOPIC = "welcome-flow"
    
    # Configuración de logs
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

settings = Settings()