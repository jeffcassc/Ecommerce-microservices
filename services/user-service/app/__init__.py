from flask import Flask
from flask_pymongo import PyMongo
import logging
from app.config import Config

# Configuración básica de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mongo = PyMongo()

def create_app():
    app = Flask(__name__)
    app.config["MONGO_URI"] = Config.MONGO_URI
    
    # Inicializar MongoDB PRIMERO
    mongo.init_app(app)
    logger.info("MongoDB initialized successfully")

    # Registrar blueprints
    from app.routes.user_routes import user_bp
    app.register_blueprint(user_bp)
    
    # Configurar manejo de errores
    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"500 Error: {str(error)}")
        return {"error": "Internal server error"}, 500
    
    @app.errorhandler(404)
    def not_found(error):
        return {"error": "Resource not found"}, 404

    # Configuración de Kafka - en segundo plano
    try:
        from app.services.kafka_service import KafkaService
        KafkaService.wait_for_kafka()
        KafkaService.create_topics()
        
        # Mover la importación aquí para evitar circularidad
        from app.services.user_service import handle_user_registration, handle_welcome_event
        KafkaService.start_consumers_in_background(
            Config.USER_TOPIC, 
            'user-service-group', 
            handle_user_registration
        )
        KafkaService.start_consumers_in_background(
            Config.WELCOME_TOPIC, 
            'welcome-service-group', 
            handle_welcome_event
        )
        
    except Exception as e:
        logger.error(f"Failed to initialize Kafka: {str(e)}")
        if app.config.get("FLASK_ENV") == "production":
            raise e
    
    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)