"""
Superset Configuration
Connects Superset to MongoDB database
"""

import os
from pathlib import Path


# Superset-specific configuration
ROW_LIMIT = 5000
SUPERSET_WEBSERVER_PORT = 8088

# Flask App Builder configuration
APP_NAME = "IoT Analytics Dashboard"

# Enable CSRF protection
WTF_CSRF_ENABLED = True
WTF_CSRF_EXEMPT_LIST = []
WTF_CSRF_TIME_LIMIT = None

# MongoDB connection
MONGODB_URI = "mongodb://localhost:27017/"
MONGODB_DATABASE = "iot_analytics"

# SQLAlchemy connection for metadata (required by Superset)
SQLALCHEMY_DATABASE_URI = "sqlite:////tmp/superset.db"

# Feature flags
FEATURE_FLAGS = {
    "ENABLE_TEMPLATE_PROCESSING": True,
}

# Cache configuration
CACHE_CONFIG = {
    "CACHE_TYPE": "simple",
    "CACHE_DEFAULT_TIMEOUT": 300,
    "CACHE_KEY_PREFIX": "superset_"
}

# MongoDB database connection for datasets
# Note: MongoDB requires a connector plugin for Superset
# For production, consider using Mongo BI Connector or similar

print("Superset configuration loaded")
print(f"MongoDB URI: {MONGODB_URI}")
print(f"Database: {MONGODB_DATABASE}")
