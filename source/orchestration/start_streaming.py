"""
Start Kafka Producer
Begins streaming IoT data to Kafka
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from kafka.kafka_producer import main as start_producer


if __name__ == "__main__":
    print("Starting Kafka Producer...")
    start_producer()
