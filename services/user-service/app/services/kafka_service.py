import time
import json
from confluent_kafka import Producer, Consumer, KafkaException
from confluent_kafka.admin import AdminClient, NewTopic
import logging
from datetime import datetime
from uuid import uuid4
from app.config import Config
from app.services.mongo_service import save_event_to_mongo

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KafkaService:
    @staticmethod
    def wait_for_kafka(max_retries=30, delay=5):
        """Espera a que Kafka esté disponible"""
        admin_client = AdminClient({'bootstrap.servers': Config.KAFKA_BROKER})
        
        for i in range(max_retries):
            try:
                # Intenta listar los topics para verificar la conexión
                admin_client.list_topics(timeout=10)
                logger.info("Successfully connected to Kafka")
                return True
            except Exception as e:
                logger.warning(f"Attempt {i+1}/{max_retries} - Kafka not ready: {str(e)}")
                time.sleep(delay)
        
        raise Exception("Failed to connect to Kafka after multiple attempts")

    @staticmethod
    def create_topics():
        """Crea los topics necesarios si no existen"""
        admin_client = AdminClient({'bootstrap.servers': Config.KAFKA_BROKER})
        
        topic_list = [
            NewTopic(Config.USER_TOPIC, num_partitions=3, replication_factor=1),
            NewTopic(Config.WELCOME_TOPIC, num_partitions=3, replication_factor=1),
            NewTopic(Config.NOTIFICATION_TOPIC, num_partitions=3, replication_factor=1)
        ]

        # Solo crea topics que no existan
        existing_topics = admin_client.list_topics(timeout=10).topics
        topics_to_create = [t for t in topic_list if t.topic not in existing_topics]
        
        if topics_to_create:
            fs = admin_client.create_topics(topics_to_create)
            for topic, f in fs.items():
                try:
                    f.result()
                    logger.info(f"Topic {topic} created")
                except Exception as e:
                    if e.args[0].code() != KafkaException.TOPIC_ALREADY_EXISTS:
                        logger.error(f"Failed to create topic {topic}: {e}")

    @staticmethod
    def get_producer():
        return Producer({
            'bootstrap.servers': Config.KAFKA_BROKER,
            'message.timeout.ms': 5000,
            'retries': 5
        })

    @staticmethod
    def produce_event(topic, source, payload, snapshot=None):
        """Produce un evento a Kafka y lo guarda en MongoDB"""
        producer = KafkaService.get_producer()
        
        event = {
            "eventId": str(uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "source": source,
            "topic": topic,
            "payload": payload,
            "snapshot": snapshot or {}
        }

        try:
            producer.produce(topic, json.dumps(event))
            producer.flush()
            logger.info(f"Event produced to {topic}: {event}")
            
            # Guardar en MongoDB
            save_event_to_mongo(event)
            
        except Exception as e:
            logger.error(f"Failed to produce event to {topic}: {str(e)}")
            raise

    @staticmethod
    def consume_events(topic, group_id, callback):
        """Consume eventos de Kafka y ejecuta el callback"""
        consumer = Consumer({
            'bootstrap.servers': Config.KAFKA_BROKER,
            'group.id': group_id,
            'auto.offset.reset': 'earliest',
            'enable.auto.commit': False
        })

        consumer.subscribe([topic])

        try:
            logger.info(f"Starting consumer for topic {topic}")
            while True:
                msg = consumer.poll(1.0)
                if msg is None:
                    continue
                if msg.error():
                    if msg.error().code() == KafkaException._PARTITION_EOF:
                        continue
                    logger.error(f"Consumer error: {msg.error()}")
                    continue

                try:
                    event = json.loads(msg.value().decode('utf-8'))
                    logger.info(f"Received event from {topic}: {event}")
                    callback(event)
                    consumer.commit(asynchronous=False)
                except Exception as e:
                    logger.error(f"Error processing message: {str(e)}")
                    
        except KeyboardInterrupt:
            pass
        finally:
            consumer.close()