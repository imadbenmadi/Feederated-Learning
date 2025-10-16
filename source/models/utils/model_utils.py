"""
Model Utilities
Shared functions for model loading, saving, and manipulation
"""

import numpy as np
import pickle
import json
from pathlib import Path
from datetime import datetime
import logging


logger = logging.getLogger(__name__)


def normalize_sensor_data(data, stats=None):
    """
    Normalize sensor data using min-max or z-score normalization
    
    Args:
        data: Array or dict of sensor values
        stats: Optional pre-computed statistics for normalization
    
    Returns:
        Normalized data and statistics
    """
    if isinstance(data, dict):
        # Convert dict to array
        values = np.array([
            data.get('temperature', 0),
            data.get('humidity', 0),
            data.get('light', 0),
            data.get('voltage', 0)
        ])
    else:
        values = np.array(data)
    
    if stats is None:
        # Compute statistics (use reasonable defaults for IoT sensors)
        stats = {
            'mean': np.array([20.0, 50.0, 500.0, 2.5]),  # temp, humidity, light, voltage
            'std': np.array([10.0, 20.0, 300.0, 0.5]),
            'min': np.array([0.0, 0.0, 0.0, 0.0]),
            'max': np.array([50.0, 100.0, 2000.0, 5.0])
        }
    
    # Z-score normalization
    normalized = (values - stats['mean']) / (stats['std'] + 1e-8)
    
    return normalized, stats


def denormalize_sensor_data(normalized_data, stats):
    """
    Denormalize sensor data back to original scale
    
    Args:
        normalized_data: Normalized array
        stats: Statistics used for normalization
    
    Returns:
        Denormalized data
    """
    denormalized = normalized_data * stats['std'] + stats['mean']
    return denormalized


def compute_model_similarity(model1_weights, model2_weights):
    """
    Compute cosine similarity between two models
    
    Args:
        model1_weights: Weights from first model
        model2_weights: Weights from second model
    
    Returns:
        Similarity score (0 to 1)
    """
    # Flatten all weights into single vectors
    def flatten_weights(weights_dict):
        flat = []
        for w in weights_dict['weights']:
            flat.extend(np.array(w).flatten())
        for b in weights_dict['biases']:
            flat.extend(np.array(b).flatten())
        return np.array(flat)
    
    vec1 = flatten_weights(model1_weights)
    vec2 = flatten_weights(model2_weights)
    
    # Cosine similarity
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    similarity = dot_product / (norm1 * norm2)
    return float(similarity)


def aggregate_model_weights(model_weights_list, weights=None):
    """
    Aggregate multiple model weights using weighted averaging (FedAvg)
    
    Args:
        model_weights_list: List of model weight dictionaries
        weights: Optional weights for each model (default: equal weights)
    
    Returns:
        Aggregated model weights
    """
    if not model_weights_list:
        return None
    
    n_models = len(model_weights_list)
    
    if weights is None:
        weights = [1.0 / n_models] * n_models
    else:
        # Normalize weights
        total = sum(weights)
        weights = [w / total for w in weights]
    
    # Initialize aggregated weights with structure from first model
    aggregated = {
        'weights': [],
        'biases': [],
        'architecture': model_weights_list[0]['architecture'].copy(),
        'timestamp': datetime.now().isoformat()
    }
    
    # Aggregate each layer
    n_layers = len(model_weights_list[0]['weights'])
    
    for layer_idx in range(n_layers):
        # Aggregate weights for this layer
        layer_weights = [
            np.array(model['weights'][layer_idx]) * w
            for model, w in zip(model_weights_list, weights)
        ]
        aggregated_layer_weights = np.sum(layer_weights, axis=0)
        
        # Aggregate biases for this layer
        layer_biases = [
            np.array(model['biases'][layer_idx]) * w
            for model, w in zip(model_weights_list, weights)
        ]
        aggregated_layer_biases = np.sum(layer_biases, axis=0)
        
        aggregated['weights'].append(aggregated_layer_weights.tolist())
        aggregated['biases'].append(aggregated_layer_biases.tolist())
    
    return aggregated


def compute_anomaly_score(actual, predicted, threshold=2.0):
    """
    Compute anomaly score based on prediction error
    
    Args:
        actual: Actual sensor values
        predicted: Predicted sensor values
        threshold: Threshold for anomaly detection (in standard deviations)
    
    Returns:
        Anomaly score and is_anomaly flag
    """
    # Compute error
    error = np.array(actual) - np.array(predicted)
    
    # Compute normalized error (z-score)
    mse = np.mean(error ** 2)
    mae = np.mean(np.abs(error))
    
    # Simple threshold-based detection
    is_anomaly = mae > threshold
    
    return {
        'mse': float(mse),
        'mae': float(mae),
        'is_anomaly': bool(is_anomaly),
        'anomaly_score': float(mae / threshold)
    }


def save_model_metadata(model_info, filepath):
    """
    Save model metadata to JSON file
    
    Args:
        model_info: Dictionary containing model information
        filepath: Path to save metadata
    """
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    with open(filepath, 'w') as f:
        json.dump(model_info, f, indent=2)
    
    logger.info(f"Model metadata saved to {filepath}")


def load_model_metadata(filepath):
    """
    Load model metadata from JSON file
    
    Args:
        filepath: Path to metadata file
    
    Returns:
        Model metadata dictionary
    """
    with open(filepath, 'r') as f:
        metadata = json.load(f)
    
    return metadata


def get_model_summary(model_weights):
    """
    Get a summary of model architecture and parameters
    
    Args:
        model_weights: Model weights dictionary
    
    Returns:
        Summary dictionary
    """
    total_params = 0
    layer_info = []
    
    for i, (w, b) in enumerate(zip(model_weights['weights'], model_weights['biases'])):
        w_array = np.array(w)
        b_array = np.array(b)
        
        layer_params = w_array.size + b_array.size
        total_params += layer_params
        
        layer_info.append({
            'layer': i,
            'weight_shape': w_array.shape,
            'bias_shape': b_array.shape,
            'parameters': layer_params
        })
    
    return {
        'architecture': model_weights['architecture'],
        'total_parameters': total_params,
        'layers': layer_info,
        'last_update': model_weights.get('timestamp', 'Unknown')
    }


def evaluate_model_performance(predictions, actuals):
    """
    Evaluate model performance using various metrics
    
    Args:
        predictions: List of predicted values
        actuals: List of actual values
    
    Returns:
        Dictionary of performance metrics
    """
    predictions = np.array(predictions)
    actuals = np.array(actuals)
    
    # Compute metrics
    mse = np.mean((predictions - actuals) ** 2)
    rmse = np.sqrt(mse)
    mae = np.mean(np.abs(predictions - actuals))
    
    # R-squared
    ss_total = np.sum((actuals - np.mean(actuals)) ** 2)
    ss_residual = np.sum((actuals - predictions) ** 2)
    r2 = 1 - (ss_residual / (ss_total + 1e-8))
    
    return {
        'mse': float(mse),
        'rmse': float(rmse),
        'mae': float(mae),
        'r2_score': float(r2)
    }
