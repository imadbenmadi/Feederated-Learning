#!/bin/bash
# Apache Superset Setup Script

echo "=========================================="
echo "Apache Superset Setup"
echo "=========================================="

# Create virtual environment for Superset
echo "Creating virtual environment..."
python -m venv superset_env

# Activate virtual environment
source superset_env/bin/activate

# Install Superset
echo "Installing Apache Superset..."
pip install apache-superset pymongo

# Initialize Superset database
echo "Initializing Superset database..."
superset db upgrade

# Create admin user
echo "Creating admin user..."
superset fab create-admin \
    --username admin \
    --firstname Admin \
    --lastname User \
    --email admin@example.com \
    --password admin

# Load examples (optional)
# superset load_examples

# Initialize Superset
superset init

echo "=========================================="
echo "✓ Superset setup complete!"
echo "=========================================="
echo "To start Superset:"
echo "  source superset_env/bin/activate"
echo "  superset run -p 8088 --with-threads --reload --debugger"
echo ""
echo "Access at: http://localhost:8088"
echo "Username: admin"
echo "Password: admin"
