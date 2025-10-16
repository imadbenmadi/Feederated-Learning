"""
Kafka Consumer Test Script
Simple consumer to test if Kafka is working correctly
"""

import json
from pathlib import Path
from kafka import KafkaConsumer
from kafka.errors import KafkaError
import logging


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_consumer():
    """
    Test Kafka consumer
    """
    # Load configuration
    config_path = Path(__file__).parent / "config" / "kafka_config.json"
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    topic_name = config['kafka']['topics']['iot_stream']['name']
    
    logger.info("=" * 60)
    logger.info("Kafka Consumer Test")
    logger.info("=" * 60)
    logger.info(f"Topic: {topic_name}")
    logger.info(f"Bootstrap servers: {config['kafka']['bootstrap_servers']}")
    
    try:
        # Create consumer
        consumer = KafkaConsumer(
            topic_name,
            bootstrap_servers=config['kafka']['bootstrap_servers'],
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id='test_consumer_group',
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )
        
        logger.info("✓ Consumer created successfully")
        logger.info("Listening for messages (press Ctrl+C to stop)...")
        logger.info("=" * 60)
        
        message_count = 0
        device_counts = {}
        
        for message in consumer:
            message_count += 1
            data = message.value
            
            device_id = data.get('device_id', 'unknown')
            device_counts[device_id] = device_counts.get(device_id, 0) + 1
            
            # Print every 10th message
            if message_count % 10 == 0:
                logger.info(f"Message #{message_count}")
                logger.info(f"  Device: {device_id}")
                logger.info(f"  Timestamp: {data.get('timestamp')}")
                logger.info(f"  Temperature: {data['sensors']['temperature']}°C")
                logger.info(f"  Humidity: {data['sensors']['humidity']}%")
                logger.info(f"  Device message counts: {device_counts}")
                logger.info("-" * 60)
    
    except KeyboardInterrupt:
        logger.info("\n" + "=" * 60)
        logger.info("Consumer stopped by user")
        logger.info(f"Total messages received: {message_count}")
        logger.info(f"Messages per device: {device_counts}")
    
    except KafkaError as e:
        logger.error(f"Kafka error: {e}")
    
    finally:
        consumer.close()
        logger.info("✓ Consumer closed")


if __name__ == "__main__":
    test_consumer()
