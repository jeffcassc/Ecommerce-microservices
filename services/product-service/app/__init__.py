from flask import Flask
from flask_pymongo import PyMongo
import logging
from shared.kafka_config import KafkaConfig
from threading import Thread
import time
from shared.kafka_service import KafkaService

import os
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

mongo = PyMongo()

def initialize_kafka():
    """Initialize Kafka in background with retries"""
    max_retries = 5
    retry_delay = 5
    
    for attempt in range(max_retries):
        try:
            KafkaService.wait_for_kafka(max_retries=10, delay=2)
            KafkaService.create_topics()
            
            # Import handlers after everything is initialized
            from app.events.product_events import (
                handle_product_created,
                handle_product_updated,
                handle_product_deleted
            )
            
            # Start consumers in separate threads
            Thread(target=lambda: KafkaService.consume_events(
                KafkaConfig.PRODUCT_EVENTS_TOPIC,
                'product-service-group',
                handle_product_created
            )).start()

            logger.info("Kafka initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Attempt {attempt + 1}/{max_retries} - Kafka initialization failed: {str(e)}")
            if attempt == max_retries - 1:
                logger.error("Max retries reached for Kafka initialization")
                raise
            time.sleep(retry_delay)

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')
    
    # Additional configuration
    app.config["MONGO_URI"] = os.getenv('MONGO_URI', 'mongodb://mongo:27017/ecommerce')
    app.config["PROPAGATE_EXCEPTIONS"] = True

    # Initialize MongoDB first
    try:
        mongo.init_app(app)
        
        # Verify MongoDB connection
        with app.app_context():
            mongo.db.command('ping')
            logger.info("MongoDB connection established successfully")
            
    except Exception as e:
        logger.error(f"MongoDB initialization failed: {str(e)}")
        raise

    # Register blueprints
    from app.routes.product_routes import product_bp
    app.register_blueprint(product_bp)
    
    # Error handling
    @app.errorhandler(400)
    def bad_request(error):
        logger.warning(f"Bad request: {str(error)}")
        return {"error": "Bad request"}, 400
    
    @app.errorhandler(404)
    def not_found(error):
        return {"error": "Resource not found"}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"500 Error: {str(error)}", exc_info=True)
        return {"error": "Internal server error"}, 500

    # Health check endpoint
    @app.route('/health')
    def health_check():
        try:
            # Check MongoDB
            with app.app_context():
                mongo.db.command('ping')
            
            # Check Kafka
            KafkaService.get_producer().list_topics(timeout=10)
                
            return {"status": "healthy", "services": ["mongodb", "kafka"]}, 200
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return {"status": "unhealthy", "error": str(e)}, 500

    # Initialize Kafka in background (with retries)
    Thread(target=initialize_kafka).start()

    logger.info("Product Service initialization completed")
    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=os.getenv('FLASK_ENV') == "development")