#!/bin/bash
# Kafka Setup Script for IoT Pipeline

echo "=========================================="
echo "Kafka Setup for IoT Streaming Pipeline"
echo "=========================================="

# Start Kafka and Zookeeper using Docker Compose
echo ""
echo "Starting Kafka and Zookeeper containers..."
docker-compose up -d

# Wait for Kafka to be ready
echo ""
echo "Waiting for Kafka to be ready..."
sleep 15

# Create Kafka topic
echo ""
echo "Creating Kafka topic 'iot_stream'..."
docker exec kafka kafka-topics --create \
    --bootstrap-server localhost:9092 \
    --replication-factor 1 \
    --partitions 3 \
    --topic iot_stream \
    --if-not-exists

# List topics to verify
echo ""
echo "Verifying topic creation..."
docker exec kafka kafka-topics --list --bootstrap-server localhost:9092

# Display topic details
echo ""
echo "Topic details:"
docker exec kafka kafka-topics --describe \
    --bootstrap-server localhost:9092 \
    --topic iot_stream

echo ""
echo "=========================================="
echo "✓ Kafka setup complete!"
echo "=========================================="
echo "Kafka UI available at: http://localhost:8080"
echo "Kafka broker: localhost:9092"
echo ""
echo "To stop: docker-compose down"
echo "To view logs: docker-compose logs -f"
