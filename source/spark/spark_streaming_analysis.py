"""
Spark Streaming Analysis
Real-time analysis of IoT data stream using the global model
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, udf
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, ArrayType
import logging
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))

from models.local.model_template import LocalNeuralNetwork
from storage.mongodb_connection import get_mongodb_connection


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SparkStreamingAnalyzer:
    """
    Streaming analysis using Spark Structured Streaming
    """
    
    def __init__(self, app_name="IoT Streaming Analysis"):
        """
        Initialize Spark streaming session
        """
        self.spark = SparkSession.builder \
            .appName(app_name) \
            .config("spark.jars.packages", 
                   "org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.0,"
                   "org.mongodb.spark:mongo-spark-connector_2.12:3.0.1") \
            .getOrCreate()
        
        self.global_model = None
        self.mongo = get_mongodb_connection()
        
        logger.info("Spark streaming session initialized")
    
    def load_global_model(self, model_path=None):
        """
        Load global model for predictions
        """
        if model_path is None:
            model_path = Path(__file__).parent.parent / "models" / "global" / "global_model_weights.pkl"
        
        logger.info(f"Loading global model from {model_path}")
        
        try:
            self.global_model = LocalNeuralNetwork.load(model_path)
            logger.info("✓ Global model loaded")
        except Exception as e:
            logger.error(f"Failed to load global model: {e}")
            # Create a default model
            self.global_model = LocalNeuralNetwork()
    
    def create_kafka_stream(self, kafka_servers, topic):
        """
        Create Kafka streaming source
        
        Args:
            kafka_servers: Kafka bootstrap servers
            topic: Kafka topic name
        
        Returns:
            Streaming DataFrame
        """
        logger.info(f"Creating Kafka stream from topic: {topic}")
        
        df = self.spark \
            .readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", kafka_servers) \
            .option("subscribe", topic) \
            .option("startingOffsets", "latest") \
            .load()
        
        # Define schema for IoT data
        schema = StructType([
            StructField("device_id", StringType()),
            StructField("timestamp", StringType()),
            StructField("sensors", StructType([
                StructField("temperature", DoubleType()),
                StructField("humidity", DoubleType()),
                StructField("light", DoubleType()),
                StructField("voltage", DoubleType())
            ]))
        ])
        
        # Parse JSON data
        parsed_df = df.select(
            from_json(col("value").cast("string"), schema).alias("data")
        ).select("data.*")
        
        return parsed_df
    
    def add_predictions(self, df):
        """
        Add model predictions to streaming DataFrame
        
        Args:
            df: Input streaming DataFrame
        
        Returns:
            DataFrame with predictions
        """
        model = self.global_model
        
        def predict_sensors(temp, humidity, light, voltage):
            """UDF for predictions"""
            if model is None:
                return [0.0, 0.0, 0.0, 0.0]
            
            try:
                import numpy as np
                X = np.array([temp, humidity, light, voltage])
                prediction = model.predict(X)
                return prediction.flatten().tolist()
            except:
                return [0.0, 0.0, 0.0, 0.0]
        
        predict_udf = udf(predict_sensors, ArrayType(DoubleType()))
        
        # Add predictions
        result_df = df.withColumn(
            "prediction",
            predict_udf(
                col("sensors.temperature"),
                col("sensors.humidity"),
                col("sensors.light"),
                col("sensors.voltage")
            )
        )
        
        # Extract components
        result_df = result_df \
            .withColumn("pred_temp", col("prediction").getItem(0)) \
            .withColumn("pred_humidity", col("prediction").getItem(1)) \
            .withColumn("pred_light", col("prediction").getItem(2)) \
            .withColumn("pred_voltage", col("prediction").getItem(3))
        
        # Calculate errors
        result_df = result_df \
            .withColumn("error_temp", 
                       col("sensors.temperature") - col("pred_temp")) \
            .withColumn("mse",
                       (col("error_temp") ** 2) / 4)
        
        return result_df
    
    def start_streaming(self, kafka_servers="localhost:9092", topic="iot_stream"):
        """
        Start streaming analysis
        
        Args:
            kafka_servers: Kafka bootstrap servers
            topic: Kafka topic to consume
        """
        logger.info("Starting streaming analysis...")
        
        # Load global model
        self.load_global_model()
        
        # Create stream
        stream_df = self.create_kafka_stream(kafka_servers, topic)
        
        # Add predictions
        predictions_df = self.add_predictions(stream_df)
        
        # Write to console (for debugging)
        console_query = predictions_df.select(
            "device_id",
            "timestamp",
            "sensors.temperature",
            "pred_temp",
            "error_temp",
            "mse"
        ).writeStream \
            .outputMode("append") \
            .format("console") \
            .option("truncate", "false") \
            .start()
        
        logger.info("✓ Streaming analysis started")
        logger.info("Results are being displayed in console")
        
        # Wait for termination
        console_query.awaitTermination()
    
    def stop(self):
        """
        Stop Spark session
        """
        self.spark.stop()
        logger.info("Spark streaming session stopped")


def main():
    """
    Main execution function
    """
    print("=" * 60)
    print("Spark Streaming Analysis")
    print("=" * 60)
    
    # Create analyzer
    analyzer = SparkStreamingAnalyzer()
    
    try:
        # Start streaming
        analyzer.start_streaming()
    
    except KeyboardInterrupt:
        logger.info("Streaming stopped by user")
    
    except Exception as e:
        logger.error(f"Streaming analysis failed: {e}")
        raise
    
    finally:
        analyzer.stop()


if __name__ == "__main__":
    main()
