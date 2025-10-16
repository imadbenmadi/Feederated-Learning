"""
Kafka Producer for IoT Data Streaming
Reads the processed dataset and streams it to Kafka topic in a continuous loop
"""

import json
import time
import pandas as pd
from pathlib import Path
from kafka import KafkaProducer
from kafka.errors import KafkaError
import logging
from datetime import datetime


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class IoTDataProducer:
    """
    Produces IoT sensor data to Kafka topic
    """
    
    def __init__(self, config_path=None):
        """
        Initialize the Kafka producer
        """
        # Load configuration
        if config_path is None:
            config_path = Path(__file__).parent / "config" / "kafka_config.json"
        
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        # Initialize Kafka producer
        self.producer = KafkaProducer(
            bootstrap_servers=self.config['kafka']['bootstrap_servers'],
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8') if k else None,
            acks=self.config['kafka']['producer']['acks'],
            retries=self.config['kafka']['producer']['retries'],
            batch_size=self.config['kafka']['producer']['batch_size'],
            linger_ms=self.config['kafka']['producer']['linger_ms']
        )
        
        self.topic_name = self.config['kafka']['topics']['iot_stream']['name']
        self.records_per_second = self.config['streaming']['records_per_second']
        self.loop_dataset = self.config['streaming']['loop_dataset']
        
        logger.info(f"Kafka Producer initialized. Topic: {self.topic_name}")
    
    def load_dataset(self, dataset_path):
        """
        Load the processed dataset
        """
        logger.info(f"Loading dataset from {dataset_path}...")
        self.df = pd.read_csv(dataset_path)
        logger.info(f"✓ Loaded {len(self.df)} records from {self.df['device_id'].nunique()} devices")
        return self.df
    
    def create_message(self, row):
        """
        Create a message from a dataframe row
        """
        message = {
            'device_id': row['device_id'],
            'timestamp': row['datetime'] if 'datetime' in row else f"{row['date']} {row['time']}",
            'epoch': int(row['epoch']),
            'sensors': {
                'temperature': float(row['temperature']),
                'humidity': float(row['humidity']),
                'light': float(row['light']),
                'voltage': float(row['voltage'])
            },
            'metadata': {
                'hour': int(row['hour']) if 'hour' in row else None,
                'day_of_week': int(row['day_of_week']) if 'day_of_week' in row else None
            },
            'ingestion_time': datetime.now().isoformat()
        }
        return message
    
    def send_message(self, message, key=None):
        """
        Send a message to Kafka topic
        """
        try:
            future = self.producer.send(
                self.topic_name,
                key=key,
                value=message
            )
            # Wait for acknowledgment (optional, for debugging)
            # record_metadata = future.get(timeout=10)
            return True
        except KafkaError as e:
            logger.error(f"Failed to send message: {e}")
            return False
    
    def stream_data(self, dataset_path):
        """
        Continuously stream data from the dataset
        """
        # Load dataset
        self.load_dataset(dataset_path)
        
        total_sent = 0
        loop_count = 0
        
        logger.info(f"Starting data stream. Rate: {self.records_per_second} records/sec")
        logger.info(f"Loop mode: {'Enabled' if self.loop_dataset else 'Disabled'}")
        logger.info("=" * 60)
        
        try:
            while True:
                loop_count += 1
                logger.info(f"Starting loop iteration #{loop_count}")
                
                for idx, row in self.df.iterrows():
                    # Create message
                    message = self.create_message(row)
                    
                    # Send to Kafka (use device_id as key for partitioning)
                    success = self.send_message(message, key=message['device_id'])
                    
                    if success:
                        total_sent += 1
                        
                        # Log progress every 100 records
                        if total_sent % 100 == 0:
                            logger.info(f"Sent {total_sent} records. Current device: {message['device_id']}")
                    
                    # Control streaming rate
                    time.sleep(1.0 / self.records_per_second)
                
                logger.info(f"Loop #{loop_count} completed. Total records sent: {total_sent}")
                
                # Check if we should loop
                if not self.loop_dataset:
                    logger.info("Loop mode disabled. Exiting...")
                    break
                
                # Small pause between loops
                time.sleep(1)
        
        except KeyboardInterrupt:
            logger.info("\nShutdown requested by user")
        finally:
            self.close()
    
    def close(self):
        """
        Close the producer connection
        """
        logger.info("Flushing remaining messages...")
        self.producer.flush()
        self.producer.close()
        logger.info("✓ Producer closed successfully")


def main():
    """
    Main execution function
    """
    print("=" * 60)
    print("IoT Data Kafka Producer")
    print("=" * 60)
    
    # Define dataset path
    dataset_path = Path(__file__).parent.parent / "data" / "processed" / "processed_iot_data.csv"
    
    # Check if dataset exists
    if not dataset_path.exists():
        logger.error(f"Dataset not found: {dataset_path}")
        logger.error("Please run data/preprocess_dataset.py first")
        return
    
    # Create and start producer
    producer = IoTDataProducer()
    producer.stream_data(dataset_path)


if __name__ == "__main__":
    main()
