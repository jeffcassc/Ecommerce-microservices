import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    KAFKA_BROKER = os.getenv('KAFKA_BROKER', 'localhost:9092')
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/ecommerce')
    USER_TOPIC = 'user-registration'
    WELCOME_TOPIC = 'welcome-flow'
    NOTIFICATION_TOPIC = 'notification-topic'