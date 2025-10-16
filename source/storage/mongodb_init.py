"""
MongoDB Initialization
Sets up collections and indexes
"""

import logging
from pathlib import Path
import json
from datetime import datetime

from mongodb_connection import get_mongodb_connection


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_schema(schema_path):
    """
    Load schema definition from JSON file
    
    Args:
        schema_path: Path to schema file
    
    Returns:
        Schema dictionary
    """
    with open(schema_path, 'r') as f:
        return json.load(f)


def initialize_collections():
    """
    Initialize MongoDB collections with validation schemas
    """
    logger.info("Initializing MongoDB collections...")
    
    # Get database connection
    mongo = get_mongodb_connection()
    db = mongo.db
    
    # Schema directory
    schema_dir = Path(__file__).parent / "schemas"
    
    # Define collections
    collections = {
        'device_data': {
            'schema_file': 'device_data_schema.json',
            'indexes': [
                ('device_id', False),
                ('timestamp', False),
                ([('device_id', 1), ('timestamp', -1)], False)
            ]
        },
        'local_models': {
            'schema_file': 'local_model_schema.json',
            'indexes': [
                ('device_id', False),
                ('timestamp', False)
            ]
        },
        'global_model': {
            'schema_file': 'global_model_schema.json',
            'indexes': [
                ('aggregation_round', True),
                ('timestamp', False)
            ]
        },
        'predictions': {
            'schema_file': 'predictions_schema.json',
            'indexes': [
                ('device_id', False),
                ('timestamp', False),
                ('prediction_type', False)
            ]
        }
    }
    
    # Create collections
    for collection_name, config in collections.items():
        logger.info(f"Setting up collection: {collection_name}")
        
        # Check if collection exists
        if collection_name not in db.list_collection_names():
            # Load schema
            schema_path = schema_dir / config['schema_file']
            if schema_path.exists():
                schema = load_schema(schema_path)
                
                # Create collection with schema validation
                db.create_collection(
                    collection_name,
                    validator={'$jsonSchema': schema}
                )
                logger.info(f"  ✓ Collection created with schema validation")
            else:
                # Create without validation
                db.create_collection(collection_name)
                logger.info(f"  ✓ Collection created")
        else:
            logger.info(f"  Collection already exists")
        
        # Create indexes
        for index_def in config['indexes']:
            if isinstance(index_def[0], list):
                keys = index_def[0]
            else:
                keys = [(index_def[0], 1)]
            
            mongo.create_index(collection_name, keys, unique=index_def[1])
    
    logger.info("✓ All collections initialized")


def insert_sample_data():
    """
    Insert sample data for testing
    """
    logger.info("Inserting sample data...")
    
    mongo = get_mongodb_connection()
    
    # Sample device data
    sample_device_data = {
        'device_id': 'device_001',
        'timestamp': datetime.now().isoformat(),
        'sensors': {
            'temperature': 22.5,
            'humidity': 45.0,
            'light': 350.0,
            'voltage': 2.8
        },
        'metadata': {
            'location': 'room_1',
            'status': 'active'
        }
    }
    
    mongo.insert_one('device_data', sample_device_data)
    logger.info("  ✓ Sample device data inserted")


def verify_setup():
    """
    Verify MongoDB setup
    """
    logger.info("Verifying MongoDB setup...")
    
    mongo = get_mongodb_connection()
    db = mongo.db
    
    # List collections
    collections = db.list_collection_names()
    logger.info(f"Collections found: {collections}")
    
    # Check indexes
    for collection_name in collections:
        indexes = db[collection_name].index_information()
        logger.info(f"{collection_name} indexes: {list(indexes.keys())}")
    
    logger.info("✓ Verification complete")


def main():
    """
    Main initialization function
    """
    print("=" * 60)
    print("MongoDB Initialization")
    print("=" * 60)
    
    try:
        # Initialize collections
        initialize_collections()
        
        # Insert sample data (optional)
        # insert_sample_data()
        
        # Verify setup
        verify_setup()
        
        print("=" * 60)
        print("✓ MongoDB initialization complete!")
        print("=" * 60)
    
    except Exception as e:
        logger.error(f"Initialization failed: {e}")
        raise


if __name__ == "__main__":
    main()
