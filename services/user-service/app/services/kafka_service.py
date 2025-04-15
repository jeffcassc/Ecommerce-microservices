from confluent_kafka import Producer, KafkaException
import json
import logging
from typing import Dict, Any
from app.config import Config
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

class KafkaEventProducer:
    def __init__(self):
        self.producer = Producer({
            'bootstrap.servers': Config.KAFKA_BOOTSTRAP_SERVERS,
            'message.timeout.ms': 5000,
            'retries': 5,
            'acks': 'all'
        })
        
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def publish_event(self, topic: str, event: Dict[str, Any]) -> bool:
        try:
            self.producer.produce(
                topic=topic,
                value=json.dumps(event).encode('utf-8'),
                callback=self._delivery_report
            )
            self.producer.flush(timeout=5)
            logger.info(f"Event published to {topic}: {event}")
            return True
        except KafkaException as e:
            logger.error(f"Failed to publish event to {topic}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error publishing event: {str(e)}")
            raise

    @staticmethod
    def _delivery_report(err, msg):
        if err is not None:
            logger.error(f"Message delivery failed: {err}")
        else:
            logger.debug(f"Message delivered to {msg.topic()} [{msg.partition()}]")

kafka_producer = KafkaEventProducer()