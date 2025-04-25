# shared/kafka_config.py
import os

class KafkaConfig:
    BROKER = os.getenv('KAFKA_BROKER', 'kafka:9092')
    
    # Topics
    USER_REGISTRATION_TOPIC = 'user-registration'
    WELCOME_TOPIC = 'welcome-flow'
    NOTIFICATION_TOPIC = 'notification-topic'
    CART_UPDATES_TOPIC = 'cart-updates'
    CART_REMOVALS_TOPIC = 'cart-removals'
    ORDER_CREATED_TOPIC = 'order-created'
    INVOICE_PROCESSING_TOPIC = 'invoice-processing'
    PRODUCT_EVENTS_TOPIC = 'product-events'
    
    @staticmethod
    def get_all_topics():
        return [
            KafkaConfig.USER_REGISTRATION_TOPIC,
            KafkaConfig.WELCOME_TOPIC,
            KafkaConfig.NOTIFICATION_TOPIC,
            KafkaConfig.CART_UPDATES_TOPIC,
            KafkaConfig.CART_REMOVALS_TOPIC,
            KafkaConfig.ORDER_CREATED_TOPIC,
            KafkaConfig.INVOICE_PROCESSING_TOPIC,
            KafkaConfig.PRODUCT_EVENTS_TOPIC
        ]