"""
Spark Batch Analysis
Performs batch analytics on the full IoT dataset using the global model
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, udf, struct
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, ArrayType
import numpy as np
import pickle
from pathlib import Path
import sys
import logging

sys.path.append(str(Path(__file__).parent.parent))

from models.local.model_template import LocalNeuralNetwork
from storage.mongodb_connection import get_mongodb_connection


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SparkBatchAnalyzer:
    """
    Batch analysis using Apache Spark and global model
    """
    
    def __init__(self, app_name="IoT Batch Analysis"):
        """
        Initialize Spark session
        """
        self.spark = SparkSession.builder \
            .appName(app_name) \
            .config("spark.mongodb.input.uri", "mongodb://localhost:27017/iot_analytics") \
            .config("spark.mongodb.output.uri", "mongodb://localhost:27017/iot_analytics") \
            .config("spark.jars.packages", "org.mongodb.spark:mongo-spark-connector_2.12:3.0.1") \
            .getOrCreate()
        
        self.global_model = None
        self.mongo = get_mongodb_connection()
        
        logger.info("Spark session initialized")
    
    def load_global_model(self, model_path=None):
        """
        Load global model for predictions
        
        Args:
            model_path: Path to global model file
        """
        if model_path is None:
            model_path = Path(__file__).parent.parent / "models" / "global" / "global_model_weights.pkl"
        
        logger.info(f"Loading global model from {model_path}")
        
        try:
            self.global_model = LocalNeuralNetwork.load(model_path)
            logger.info("✓ Global model loaded")
        except Exception as e:
            logger.error(f"Failed to load global model: {e}")
            raise
    
    def load_dataset(self, dataset_path):
        """
        Load IoT dataset into Spark DataFrame
        
        Args:
            dataset_path: Path to processed dataset
        
        Returns:
            Spark DataFrame
        """
        logger.info(f"Loading dataset from {dataset_path}")
        
        df = self.spark.read.csv(
            str(dataset_path),
            header=True,
            inferSchema=True
        )
        
        logger.info(f"✓ Loaded {df.count()} records")
        
        return df
    
    def create_prediction_udf(self):
        """
        Create UDF for model predictions
        
        Returns:
            Spark UDF
        """
        model = self.global_model
        
        def predict_sensors(temp, humidity, light, voltage):
            """
            Make prediction using global model
            """
            if model is None:
                return [0.0, 0.0, 0.0, 0.0]
            
            try:
                X = np.array([temp, humidity, light, voltage])
                prediction = model.predict(X)
                return prediction.flatten().tolist()
            except:
                return [0.0, 0.0, 0.0, 0.0]
        
        return udf(predict_sensors, ArrayType(DoubleType()))
    
    def analyze_batch(self, dataset_path):
        """
        Perform batch analysis on dataset
        
        Args:
            dataset_path: Path to dataset
        
        Returns:
            Analysis results DataFrame
        """
        logger.info("Starting batch analysis...")
        
        # Load dataset
        df = self.load_dataset(dataset_path)
        
        # Load global model
        self.load_global_model()
        
        # Create prediction UDF
        predict_udf = self.create_prediction_udf()
        
        # Make predictions
        logger.info("Making predictions...")
        predictions_df = df.withColumn(
            "prediction",
            predict_udf(
                col("temperature"),
                col("humidity"),
                col("light"),
                col("voltage")
            )
        )
        
        # Extract prediction components
        predictions_df = predictions_df \
            .withColumn("pred_temp", col("prediction").getItem(0)) \
            .withColumn("pred_humidity", col("prediction").getItem(1)) \
            .withColumn("pred_light", col("prediction").getItem(2)) \
            .withColumn("pred_voltage", col("prediction").getItem(3))
        
        # Calculate errors
        predictions_df = predictions_df \
            .withColumn("error_temp", col("temperature") - col("pred_temp")) \
            .withColumn("error_humidity", col("humidity") - col("pred_humidity")) \
            .withColumn("error_light", col("light") - col("pred_light")) \
            .withColumn("error_voltage", col("voltage") - col("pred_voltage"))
        
        # Calculate MSE per record
        predictions_df = predictions_df.withColumn(
            "mse",
            (col("error_temp") ** 2 + col("error_humidity") ** 2 + 
             col("error_light") ** 2 + col("error_voltage") ** 2) / 4
        )
        
        logger.info("✓ Predictions complete")
        
        # Compute statistics
        self.compute_statistics(predictions_df)
        
        # Save results to MongoDB
        self.save_to_mongodb(predictions_df, "batch")
        
        return predictions_df
    
    def compute_statistics(self, df):
        """
        Compute and display statistics
        
        Args:
            df: Predictions DataFrame
        """
        logger.info("=" * 60)
        logger.info("Batch Analysis Statistics")
        logger.info("=" * 60)
        
        # Overall statistics
        stats = df.select(
            "mse",
            "error_temp",
            "error_humidity",
            "error_light",
            "error_voltage"
        ).describe()
        
        stats.show()
        
        # Per-device statistics
        logger.info("\nPer-Device Statistics:")
        device_stats = df.groupBy("device_id").agg({
            "mse": "avg",
            "error_temp": "avg",
            "error_humidity": "avg"
        })
        
        device_stats.show()
    
    def save_to_mongodb(self, df, prediction_type="batch"):
        """
        Save predictions to MongoDB
        
        Args:
            df: Predictions DataFrame
            prediction_type: Type of prediction (batch/streaming)
        """
        logger.info(f"Saving {prediction_type} predictions to MongoDB...")
        
        try:
            # Convert to Pandas for easier MongoDB insertion
            pandas_df = df.select(
                "device_id",
                "datetime",
                "temperature",
                "humidity",
                "light",
                "voltage",
                "pred_temp",
                "pred_humidity",
                "pred_light",
                "pred_voltage",
                "mse"
            ).limit(10000).toPandas()  # Limit for performance
            
            # Prepare documents
            documents = []
            for _, row in pandas_df.iterrows():
                doc = {
                    'device_id': row['device_id'],
                    'timestamp': str(row['datetime']),
                    'prediction_type': prediction_type,
                    'actual': {
                        'temperature': float(row['temperature']),
                        'humidity': float(row['humidity']),
                        'light': float(row['light']),
                        'voltage': float(row['voltage'])
                    },
                    'predicted': {
                        'temperature': float(row['pred_temp']),
                        'humidity': float(row['pred_humidity']),
                        'light': float(row['pred_light']),
                        'voltage': float(row['pred_voltage'])
                    },
                    'error_metrics': {
                        'mse': float(row['mse'])
                    },
                    'is_anomaly': float(row['mse']) > 10.0  # Simple threshold
                }
                documents.append(doc)
            
            # Insert into MongoDB
            self.mongo.insert_many('predictions', documents)
            
            logger.info(f"✓ Saved {len(documents)} predictions to MongoDB")
        
        except Exception as e:
            logger.error(f"Failed to save to MongoDB: {e}")
    
    def stop(self):
        """
        Stop Spark session
        """
        self.spark.stop()
        logger.info("Spark session stopped")


def main():
    """
    Main execution function
    """
    print("=" * 60)
    print("Spark Batch Analysis")
    print("=" * 60)
    
    # Dataset path
    dataset_path = Path(__file__).parent.parent / "data" / "processed" / "processed_iot_data.csv"
    
    if not dataset_path.exists():
        logger.error(f"Dataset not found: {dataset_path}")
        return
    
    # Create analyzer
    analyzer = SparkBatchAnalyzer()
    
    try:
        # Perform batch analysis
        results = analyzer.analyze_batch(dataset_path)
        
        logger.info("\n" + "=" * 60)
        logger.info("✓ Batch analysis complete!")
        logger.info("=" * 60)
    
    except Exception as e:
        logger.error(f"Batch analysis failed: {e}")
        raise
    
    finally:
        analyzer.stop()


if __name__ == "__main__":
    main()
