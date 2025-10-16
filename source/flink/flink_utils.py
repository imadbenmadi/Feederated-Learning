"""
Flink Utilities
Helper functions for state management and data processing
"""

import json
import numpy as np
from datetime import datetime
import logging


logger = logging.getLogger(__name__)


def serialize_state(obj):
    """
    Serialize object for Flink state storage
    
    Args:
        obj: Object to serialize
    
    Returns:
        Serialized bytes
    """
    import pickle
    return pickle.dumps(obj)


def deserialize_state(data):
    """
    Deserialize object from Flink state
    
    Args:
        data: Serialized bytes
    
    Returns:
        Deserialized object
    """
    import pickle
    return pickle.loads(data)


def aggregate_device_metrics(metrics_list):
    """
    Aggregate metrics from multiple devices
    
    Args:
        metrics_list: List of metric dictionaries
    
    Returns:
        Aggregated metrics
    """
    if not metrics_list:
        return {}
    
    # Compute averages
    total_loss = sum(m.get('loss', 0) for m in metrics_list)
    avg_loss = total_loss / len(metrics_list)
    
    return {
        'num_devices': len(metrics_list),
        'average_loss': avg_loss,
        'total_updates': sum(m.get('training_count', 0) for m in metrics_list),
        'timestamp': datetime.now().isoformat()
    }


def create_sliding_window(data_buffer, window_size=100):
    """
    Create sliding window from data buffer
    
    Args:
        data_buffer: List of data points
        window_size: Size of sliding window
    
    Returns:
        Windowed data
    """
    if len(data_buffer) <= window_size:
        return data_buffer
    else:
        return data_buffer[-window_size:]


def compute_data_statistics(data_list, feature_names):
    """
    Compute statistics for sensor data
    
    Args:
        data_list: List of sensor reading dictionaries
        feature_names: List of feature names
    
    Returns:
        Statistics dictionary
    """
    if not data_list:
        return {}
    
    stats = {}
    
    for feature in feature_names:
        values = [d.get(feature, 0) for d in data_list]
        stats[feature] = {
            'mean': np.mean(values),
            'std': np.std(values),
            'min': np.min(values),
            'max': np.max(values)
        }
    
    return stats
