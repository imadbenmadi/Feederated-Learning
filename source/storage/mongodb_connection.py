"""
MongoDB Connection Manager
Handles database connections and operations
"""

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import logging
from pathlib import Path
import json


logger = logging.getLogger(__name__)


class MongoDBConnection:
    """
    MongoDB connection manager
    """
    
    def __init__(self, config_path=None):
        """
        Initialize MongoDB connection
        
        Args:
            config_path: Path to MongoDB configuration file
        """
        if config_path is None:
            config_path = Path(__file__).parent / "mongo_config.json"
        
        # Load configuration
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        self.client = None
        self.db = None
        
        self.connect()
    
    def connect(self):
        """
        Establish connection to MongoDB
        """
        try:
            mongo_uri = self.config['mongodb']['uri']
            db_name = self.config['mongodb']['database']
            
            self.client = MongoClient(
                mongo_uri,
                serverSelectionTimeoutMS=5000
            )
            
            # Test connection
            self.client.admin.command('ping')
            
            self.db = self.client[db_name]
            
            logger.info(f"✓ Connected to MongoDB database: {db_name}")
            
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    def get_collection(self, collection_name):
        """
        Get a collection from the database
        
        Args:
            collection_name: Name of the collection
        
        Returns:
            MongoDB collection object
        """
        if self.db is None:
            raise Exception("Not connected to database")
        
        return self.db[collection_name]
    
    def insert_one(self, collection_name, document):
        """
        Insert a single document
        
        Args:
            collection_name: Name of collection
            document: Document to insert
        
        Returns:
            Inserted ID
        """
        collection = self.get_collection(collection_name)
        result = collection.insert_one(document)
        return result.inserted_id
    
    def insert_many(self, collection_name, documents):
        """
        Insert multiple documents
        
        Args:
            collection_name: Name of collection
            documents: List of documents to insert
        
        Returns:
            List of inserted IDs
        """
        collection = self.get_collection(collection_name)
        result = collection.insert_many(documents)
        return result.inserted_ids
    
    def find(self, collection_name, query={}, projection=None, limit=None):
        """
        Find documents matching query
        
        Args:
            collection_name: Name of collection
            query: Query dictionary
            projection: Fields to include/exclude
            limit: Maximum number of documents to return
        
        Returns:
            List of documents
        """
        collection = self.get_collection(collection_name)
        cursor = collection.find(query, projection)
        
        if limit:
            cursor = cursor.limit(limit)
        
        return list(cursor)
    
    def find_one(self, collection_name, query):
        """
        Find a single document
        
        Args:
            collection_name: Name of collection
            query: Query dictionary
        
        Returns:
            Document or None
        """
        collection = self.get_collection(collection_name)
        return collection.find_one(query)
    
    def update_one(self, collection_name, query, update):
        """
        Update a single document
        
        Args:
            collection_name: Name of collection
            query: Query to find document
            update: Update operations
        
        Returns:
            Number of modified documents
        """
        collection = self.get_collection(collection_name)
        result = collection.update_one(query, update)
        return result.modified_count
    
    def delete_many(self, collection_name, query):
        """
        Delete multiple documents
        
        Args:
            collection_name: Name of collection
            query: Query to match documents
        
        Returns:
            Number of deleted documents
        """
        collection = self.get_collection(collection_name)
        result = collection.delete_many(query)
        return result.deleted_count
    
    def create_index(self, collection_name, keys, unique=False):
        """
        Create an index on a collection
        
        Args:
            collection_name: Name of collection
            keys: Index keys
            unique: Whether index should be unique
        """
        collection = self.get_collection(collection_name)
        collection.create_index(keys, unique=unique)
        logger.info(f"Index created on {collection_name}: {keys}")
    
    def close(self):
        """
        Close the database connection
        """
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")


# Singleton instance
_mongo_connection = None


def get_mongodb_connection(config_path=None):
    """
    Get MongoDB connection (singleton)
    
    Args:
        config_path: Path to configuration file
    
    Returns:
        MongoDBConnection instance
    """
    global _mongo_connection
    
    if _mongo_connection is None:
        _mongo_connection = MongoDBConnection(config_path)
    
    return _mongo_connection
