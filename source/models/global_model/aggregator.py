"""
Model Aggregator
Handles the aggregation logic for federated learning
"""

import numpy as np
from datetime import datetime
import logging
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))
from models.utils.model_utils import aggregate_model_weights, compute_model_similarity


logger = logging.getLogger(__name__)


class ModelAggregator:
    """
    Aggregates local model updates using various strategies
    """
    
    def __init__(self, aggregation_strategy='fedavg'):
        """
        Initialize aggregator
        
        Args:
            aggregation_strategy: Strategy for aggregation
                - 'fedavg': Federated averaging (weighted by samples)
                - 'equal': Simple averaging with equal weights
                - 'weighted': Custom weighted averaging
                - 'median': Coordinate-wise median
        """
        self.aggregation_strategy = aggregation_strategy
        self.aggregation_count = 0
        
        logger.info(f"Model aggregator initialized with strategy: {aggregation_strategy}")
    
    def federated_averaging(self, model_updates):
        """
        FedAvg algorithm - weighted by number of samples
        
        Args:
            model_updates: List of model update dictionaries
        
        Returns:
            Aggregated model weights
        """
        if not model_updates:
            return None
        
        # Extract sample counts
        sample_counts = [update.get('sample_count', 1) for update in model_updates]
        total_samples = sum(sample_counts)
        
        # Compute weights proportional to sample counts
        weights = [count / total_samples for count in sample_counts]
        
        # Extract model weights
        model_weights_list = [update['weights'] for update in model_updates]
        
        # Aggregate
        aggregated = aggregate_model_weights(model_weights_list, weights)
        
        logger.info(f"FedAvg aggregation: {len(model_updates)} models, {total_samples} total samples")
        
        return aggregated
    
    def equal_averaging(self, model_updates):
        """
        Simple averaging with equal weights
        
        Args:
            model_updates: List of model update dictionaries
        
        Returns:
            Aggregated model weights
        """
        if not model_updates:
            return None
        
        model_weights_list = [update['weights'] for update in model_updates]
        aggregated = aggregate_model_weights(model_weights_list, weights=None)
        
        logger.info(f"Equal averaging: {len(model_updates)} models")
        
        return aggregated
    
    def weighted_averaging(self, model_updates):
        """
        Weighted averaging with custom weights
        
        Args:
            model_updates: List of model update dictionaries with 'weight' field
        
        Returns:
            Aggregated model weights
        """
        if not model_updates:
            return None
        
        # Extract custom weights
        custom_weights = [update.get('weight', 1.0) for update in model_updates]
        model_weights_list = [update['weights'] for update in model_updates]
        
        aggregated = aggregate_model_weights(model_weights_list, custom_weights)
        
        logger.info(f"Weighted averaging: {len(model_updates)} models")
        
        return aggregated
    
    def median_aggregation(self, model_updates):
        """
        Coordinate-wise median aggregation (more robust to outliers)
        
        Args:
            model_updates: List of model update dictionaries
        
        Returns:
            Aggregated model weights
        """
        if not model_updates:
            return None
        
        model_weights_list = [update['weights'] for update in model_updates]
        
        # Initialize aggregated structure
        aggregated = {
            'weights': [],
            'biases': [],
            'architecture': model_weights_list[0]['architecture'].copy(),
            'timestamp': datetime.now().isoformat()
        }
        
        # Compute median for each layer
        n_layers = len(model_weights_list[0]['weights'])
        
        for layer_idx in range(n_layers):
            # Stack weights from all models
            layer_weights_stack = np.array([
                np.array(model['weights'][layer_idx])
                for model in model_weights_list
            ])
            
            layer_biases_stack = np.array([
                np.array(model['biases'][layer_idx])
                for model in model_weights_list
            ])
            
            # Compute median
            median_weights = np.median(layer_weights_stack, axis=0)
            median_biases = np.median(layer_biases_stack, axis=0)
            
            aggregated['weights'].append(median_weights.tolist())
            aggregated['biases'].append(median_biases.tolist())
        
        logger.info(f"Median aggregation: {len(model_updates)} models")
        
        return aggregated
    
    def aggregate(self, model_updates):
        """
        Aggregate model updates using configured strategy
        
        Args:
            model_updates: List of model update dictionaries
        
        Returns:
            Aggregated model weights and metadata
        """
        if not model_updates:
            logger.warning("No model updates to aggregate")
            return None, None
        
        # Select aggregation method
        if self.aggregation_strategy == 'fedavg':
            aggregated = self.federated_averaging(model_updates)
        elif self.aggregation_strategy == 'equal':
            aggregated = self.equal_averaging(model_updates)
        elif self.aggregation_strategy == 'weighted':
            aggregated = self.weighted_averaging(model_updates)
        elif self.aggregation_strategy == 'median':
            aggregated = self.median_aggregation(model_updates)
        else:
            logger.error(f"Unknown aggregation strategy: {self.aggregation_strategy}")
            return None, None
        
        # Create metadata
        metadata = {
            'aggregation_round': self.aggregation_count,
            'timestamp': datetime.now().isoformat(),
            'strategy': self.aggregation_strategy,
            'num_models': len(model_updates),
            'device_ids': [u['device_id'] for u in model_updates],
            'total_samples': sum([u.get('sample_count', 0) for u in model_updates])
        }
        
        self.aggregation_count += 1
        
        return aggregated, metadata
    
    def compute_consensus_score(self, model_updates):
        """
        Compute consensus score among local models
        
        Args:
            model_updates: List of model update dictionaries
        
        Returns:
            Consensus score (0 to 1)
        """
        if len(model_updates) < 2:
            return 1.0
        
        # Compute pairwise similarities
        similarities = []
        model_weights_list = [u['weights'] for u in model_updates]
        
        for i in range(len(model_weights_list)):
            for j in range(i + 1, len(model_weights_list)):
                sim = compute_model_similarity(
                    model_weights_list[i],
                    model_weights_list[j]
                )
                similarities.append(sim)
        
        # Average similarity
        consensus = np.mean(similarities) if similarities else 0.0
        
        logger.info(f"Model consensus score: {consensus:.4f}")
        
        return float(consensus)
