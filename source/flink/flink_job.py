"""
Apache Flink Streaming Job
Consumes IoT data from Kafka and performs per-device local model training
"""

import json
import logging
from pathlib import Path
import sys

# Note: This uses PyFlink for Python-based Flink jobs
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors import FlinkKafkaConsumer
from pyflink.common.serialization import SimpleStringSchema
from pyflink.common.typeinfo import Types
from pyflink.datastream.functions import MapFunction, KeyedProcessFunction
from pyflink.datastream.state import ValueStateDescriptor

sys.path.append(str(Path(__file__).parent.parent))

from flink.flink_local_model_manager import LocalModelManager


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class IoTDataParser(MapFunction):
    """
    Parse incoming Kafka messages
    """
    
    def map(self, value):
        """
        Parse JSON message from Kafka
        """
        try:
            data = json.loads(value)
            return data
        except Exception as e:
            logger.error(f"Failed to parse message: {e}")
            return None


class DeviceModelTrainer(KeyedProcessFunction):
    """
    Processes data per device and trains local models
    """
    
    def __init__(self, global_server_url):
        self.global_server_url = global_server_url
        self.model_manager = None
    
    def open(self, runtime_context):
        """
        Initialize per-device state
        """
        # Create state for model manager
        self.model_manager_state = runtime_context.get_state(
            ValueStateDescriptor("model_manager", Types.PICKLED_BYTE_ARRAY())
        )
        
        # Initialize or load model manager
        manager = self.model_manager_state.value()
        if manager is None:
            self.model_manager = LocalModelManager(
                global_server_url=self.global_server_url
            )
        else:
            self.model_manager = manager
        
        logger.info("Device model trainer initialized")
    
    def process_element(self, value, ctx):
        """
        Process incoming sensor data for a device
        """
        if value is None:
            return
        
        device_id = value.get('device_id')
        sensors = value.get('sensors', {})
        timestamp = value.get('timestamp')
        
        if not device_id or not sensors:
            return
        
        # Train local model
        result = self.model_manager.process_data(device_id, sensors, timestamp)
        
        # Update state
        self.model_manager_state.update(self.model_manager)
        
        # Yield result
        if result:
            yield result


def create_flink_job(kafka_config, global_server_url):
    """
    Create and configure Flink streaming job
    
    Args:
        kafka_config: Kafka configuration dictionary
        global_server_url: URL of global model server
    
    Returns:
        Configured Flink job
    """
    # Create execution environment
    env = StreamExecutionEnvironment.get_execution_environment()
    env.set_parallelism(3)  # Match Kafka partitions
    
    # Add Kafka connector JAR
    env.add_jars("file:///path/to/flink-sql-connector-kafka.jar")
    
    # Configure Kafka consumer
    kafka_props = {
        'bootstrap.servers': ','.join(kafka_config['bootstrap_servers']),
        'group.id': kafka_config['consumer']['group_id'],
        'auto.offset.reset': kafka_config['consumer']['auto_offset_reset']
    }
    
    topic_name = kafka_config['topics']['iot_stream']['name']
    
    # Create Kafka consumer
    kafka_consumer = FlinkKafkaConsumer(
        topics=topic_name,
        deserialization_schema=SimpleStringSchema(),
        properties=kafka_props
    )
    
    # Build streaming pipeline
    stream = env.add_source(kafka_consumer)
    
    # Parse JSON messages
    parsed_stream = stream.map(IoTDataParser(), output_type=Types.PICKLED_BYTE_ARRAY())
    
    # Key by device_id and process
    device_stream = parsed_stream \
        .key_by(lambda x: x.get('device_id') if x else 'unknown') \
        .process(DeviceModelTrainer(global_server_url))
    
    # Print results (for debugging)
    device_stream.print()
    
    return env


def main():
    """
    Main execution function
    """
    print("=" * 60)
    print("Flink IoT Streaming Job")
    print("=" * 60)
    
    # Load configurations
    config_path = Path(__file__).parent.parent / "kafka" / "config" / "kafka_config.json"
    with open(config_path, 'r') as f:
        kafka_config = json.load(f)['kafka']
    
    global_server_url = "http://localhost:8000"  # Default global server URL
    
    # Create Flink job
    env = create_flink_job(kafka_config, global_server_url)
    
    # Execute job
    logger.info("Starting Flink streaming job...")
    try:
        env.execute("IoT Local Model Training Job")
    except KeyboardInterrupt:
        logger.info("Job stopped by user")


if __name__ == "__main__":
    main()
