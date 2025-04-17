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
    
    # Inicializar MongoDB
    mongo.init_app(app)
    
    # Configuración de Kafka
    try:
        from app.services.kafka_service import KafkaService
        
        # Esperar a que Kafka esté listo
        KafkaService.wait_for_kafka()
        
        # Crear topics si no existen
        KafkaService.create_topics()
        
        # Importar e iniciar consumidores (en segundo plano)
        from app.events.user_events import start_event_consumers
        start_event_consumers()
        
    except Exception as e:
        logger.error(f"Failed to initialize Kafka: {str(e)}")
        # Puedes decidir si quieres que la app falle completamente o continúe
        # raise e  # Descomenta si quieres que falle si Kafka no está disponible
    
    # Registrar blueprints (import aquí para evitar circular imports)
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
    
    logger.info("Application initialized successfully")
    return app

# Crear la aplicación Flask
app = create_app()