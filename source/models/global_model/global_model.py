"""
Global Model Definition and Management
Handles the aggregated global model for federated learning
"""

import numpy as np
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from local.model_template import LocalNeuralNetwork
from models.utils.model_utils import aggregate_model_weights, get_model_summary
import logging


logger = logging.getLogger(__name__)


class GlobalModel:
    """
    Global model that aggregates updates from local device models
    """
    
    def __init__(self, input_size=4, hidden_sizes=[16, 8], output_size=4, learning_rate=0.01):
        """
        Initialize global model with same architecture as local models
        """
        self.model = LocalNeuralNetwork(
            input_size=input_size,
            hidden_sizes=hidden_sizes,
            output_size=output_size,
            learning_rate=learning_rate
        )
        
        self.aggregation_history = []
        self.device_contributions = {}
        
        logger.info("Global model initialized")
        logger.info(f"Architecture: {input_size} -> {hidden_sizes} -> {output_size}")
    
    def aggregate_updates(self, local_model_updates, aggregation_strategy='fedavg'):
        """
        Aggregate local model updates into the global model
        
        Args:
            local_model_updates: List of dictionaries containing:
                - device_id: Device identifier
                - weights: Model weights
                - sample_count: Number of samples used for training
                - timestamp: Update timestamp
            aggregation_strategy: Strategy for aggregation ('fedavg', 'weighted', 'median')
        
        Returns:
            Aggregation metadata
        """
        if not local_model_updates:
            logger.warning("No local updates to aggregate")
            return None
        
        logger.info(f"Aggregating {len(local_model_updates)} local model updates")
        
        # Extract weights and compute aggregation weights
        model_weights_list = [update['weights'] for update in local_model_updates]
        
        if aggregation_strategy == 'fedavg':
            # Weighted by number of samples
            sample_counts = [update.get('sample_count', 1) for update in local_model_updates]
            total_samples = sum(sample_counts)
            weights = [count / total_samples for count in sample_counts]
        elif aggregation_strategy == 'weighted':
            # Custom weights based on device performance
            weights = [update.get('weight', 1.0) for update in local_model_updates]
        else:
            # Equal weights
            weights = None
        
        # Perform aggregation
        aggregated_weights = aggregate_model_weights(model_weights_list, weights)
        
        if aggregated_weights:
            # Update global model
            self.model.set_weights(aggregated_weights)
            
            # Record aggregation metadata
            aggregation_meta = {
                'timestamp': aggregated_weights['timestamp'],
                'num_devices': len(local_model_updates),
                'device_ids': [u['device_id'] for u in local_model_updates],
                'total_samples': sum([u.get('sample_count', 0) for u in local_model_updates]),
                'aggregation_strategy': aggregation_strategy
            }
            
            self.aggregation_history.append(aggregation_meta)
            
            # Update device contribution tracking
            for update in local_model_updates:
                device_id = update['device_id']
                if device_id not in self.device_contributions:
                    self.device_contributions[device_id] = 0
                self.device_contributions[device_id] += 1
            
            logger.info(f"✓ Global model updated. Round #{len(self.aggregation_history)}")
            logger.info(f"  Participating devices: {aggregation_meta['device_ids']}")
            
            return aggregation_meta
        
        return None
    
    def get_global_weights(self):
        """
        Get current global model weights
        
        Returns:
            Global model weights dictionary
        """
        return self.model.get_weights()
    
    def predict(self, X):
        """
        Make prediction using global model
        
        Args:
            X: Input data
        
        Returns:
            Predictions
        """
        return self.model.predict(X)
    
    def evaluate(self, X, y):
        """
        Evaluate global model performance
        
        Args:
            X: Input data
            y: True labels
        
        Returns:
            Evaluation metrics
        """
        predictions = self.predict(X)
        
        # Compute metrics
        mse = np.mean((predictions - y) ** 2)
        mae = np.mean(np.abs(predictions - y))
        
        return {
            'mse': float(mse),
            'mae': float(mae),
            'samples_evaluated': len(X)
        }
    
    def save(self, filepath):
        """
        Save global model to file
        
        Args:
            filepath: Path to save the model
        """
        self.model.save(filepath)
        logger.info(f"Global model saved to {filepath}")
    
    def load(self, filepath):
        """
        Load global model from file
        
        Args:
            filepath: Path to load model from
        """
        self.model = LocalNeuralNetwork.load(filepath)
        logger.info(f"Global model loaded from {filepath}")
    
    def get_summary(self):
        """
        Get summary of global model
        
        Returns:
            Summary dictionary
        """
        weights = self.get_global_weights()
        summary = get_model_summary(weights)
        
        summary['aggregation_rounds'] = len(self.aggregation_history)
        summary['total_device_contributions'] = sum(self.device_contributions.values())
        summary['unique_devices'] = len(self.device_contributions)
        summary['device_contributions'] = self.device_contributions
        
        return summary
