"""
Local Model Manager for Flink
Handles per-device model creation, training, and updates
"""

import numpy as np
from datetime import datetime
import logging
from pathlib import Path
import sys
import requests

sys.path.append(str(Path(__file__).parent.parent))

from models.local.model_template import LocalNeuralNetwork, create_training_data


logger = logging.getLogger(__name__)


class LocalModelManager:
    """
    Manages local models for multiple devices in Flink
    """
    
    def __init__(self, global_server_url=None, update_frequency=100):
        """
        Initialize model manager
        
        Args:
            global_server_url: URL of global model aggregation server
            update_frequency: Send updates every N training steps
        """
        self.device_models = {}
        self.device_data_buffers = {}
        self.training_counts = {}
        self.global_server_url = global_server_url
        self.update_frequency = update_frequency
        
        logger.info("Local model manager initialized")
    
    def get_or_create_model(self, device_id):
        """
        Get existing model or create new one for device
        
        Args:
            device_id: Device identifier
        
        Returns:
            Local neural network model
        """
        if device_id not in self.device_models:
            logger.info(f"Creating new model for device: {device_id}")
            model = LocalNeuralNetwork(
                input_size=4,
                hidden_sizes=[16, 8],
                output_size=4,
                learning_rate=0.01
            )
            self.device_models[device_id] = model
            self.training_counts[device_id] = 0
            self.device_data_buffers[device_id] = []
        
        return self.device_models[device_id]
    
    def process_data(self, device_id, sensors, timestamp):
        """
        Process incoming sensor data for a device
        
        Args:
            device_id: Device identifier
            sensors: Sensor readings dictionary
            timestamp: Data timestamp
        
        Returns:
            Processing result dictionary
        """
        # Get or create model
        model = self.get_or_create_model(device_id)
        
        # Add to buffer
        self.device_data_buffers[device_id].append({
            'sensors': sensors,
            'timestamp': timestamp
        })
        
        # Keep only recent data (sliding window)
        if len(self.device_data_buffers[device_id]) > 1000:
            self.device_data_buffers[device_id].pop(0)
        
        # Prepare training data
        buffer = self.device_data_buffers[device_id]
        
        if len(buffer) >= 2:
            # Use current and previous reading for training
            current = buffer[-1]['sensors']
            previous = buffer[-2]['sensors']
            
            X, y = create_training_data(previous, current)
            
            # Train model
            loss = model.train_step(X, y)
            
            self.training_counts[device_id] += 1
            
            # Check if we should send update to global server
            should_update = self.training_counts[device_id] % self.update_frequency == 0
            
            if should_update and self.global_server_url:
                self.send_model_update(device_id, model)
            
            # Make prediction
            prediction = model.predict(X)
            
            return {
                'device_id': device_id,
                'timestamp': timestamp,
                'sensors': sensors,
                'prediction': prediction.tolist(),
                'loss': float(loss),
                'training_count': self.training_counts[device_id],
                'update_sent': should_update
            }
        
        return None
    
    def send_model_update(self, device_id, model):
        """
        Send model update to global server
        
        Args:
            device_id: Device identifier
            model: Local neural network model
        """
        try:
            weights = model.get_weights()
            
            update_data = {
                'device_id': device_id,
                'weights': weights,
                'sample_count': self.training_counts[device_id],
                'timestamp': datetime.now().isoformat()
            }
            
            response = requests.post(
                f"{self.global_server_url}/api/local-update",
                json=update_data,
                timeout=5
            )
            
            if response.status_code == 200:
                logger.info(f"✓ Model update sent for {device_id}")
            else:
                logger.warning(f"Failed to send update for {device_id}: {response.status_code}")
        
        except Exception as e:
            logger.error(f"Error sending model update for {device_id}: {e}")
    
    def get_global_model(self):
        """
        Fetch latest global model from server
        
        Returns:
            Global model weights or None
        """
        if not self.global_server_url:
            return None
        
        try:
            response = requests.get(
                f"{self.global_server_url}/api/global-model",
                timeout=5
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"Failed to fetch global model: {response.status_code}")
                return None
        
        except Exception as e:
            logger.error(f"Error fetching global model: {e}")
            return None
    
    def update_from_global(self, device_id, global_weights):
        """
        Update local model with global weights
        
        Args:
            device_id: Device identifier
            global_weights: Global model weights
        """
        if device_id in self.device_models:
            self.device_models[device_id].set_weights(global_weights)
            logger.info(f"✓ Updated {device_id} with global model")
    
    def get_stats(self):
        """
        Get statistics about managed models
        
        Returns:
            Statistics dictionary
        """
        return {
            'total_devices': len(self.device_models),
            'device_ids': list(self.device_models.keys()),
            'training_counts': self.training_counts,
            'buffer_sizes': {
                device_id: len(buffer)
                for device_id, buffer in self.device_data_buffers.items()
            }
        }
