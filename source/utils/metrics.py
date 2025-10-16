"""
Metrics Utilities
Functions for computing and evaluating model metrics
"""

import numpy as np
from typing import Dict, List, Tuple


def compute_mse(actual: np.ndarray, predicted: np.ndarray) -> float:
    """
    Compute Mean Squared Error
    
    Args:
        actual: Actual values
        predicted: Predicted values
    
    Returns:
        MSE value
    """
    return float(np.mean((actual - predicted) ** 2))


def compute_rmse(actual: np.ndarray, predicted: np.ndarray) -> float:
    """
    Compute Root Mean Squared Error
    
    Args:
        actual: Actual values
        predicted: Predicted values
    
    Returns:
        RMSE value
    """
    return float(np.sqrt(compute_mse(actual, predicted)))


def compute_mae(actual: np.ndarray, predicted: np.ndarray) -> float:
    """
    Compute Mean Absolute Error
    
    Args:
        actual: Actual values
        predicted: Predicted values
    
    Returns:
        MAE value
    """
    return float(np.mean(np.abs(actual - predicted)))


def compute_r2_score(actual: np.ndarray, predicted: np.ndarray) -> float:
    """
    Compute R-squared score
    
    Args:
        actual: Actual values
        predicted: Predicted values
    
    Returns:
        R² score
    """
    ss_total = np.sum((actual - np.mean(actual)) ** 2)
    ss_residual = np.sum((actual - predicted) ** 2)
    
    if ss_total == 0:
        return 0.0
    
    return float(1 - (ss_residual / ss_total))


def compute_all_metrics(actual: np.ndarray, predicted: np.ndarray) -> Dict[str, float]:
    """
    Compute all regression metrics
    
    Args:
        actual: Actual values
        predicted: Predicted values
    
    Returns:
        Dictionary of metrics
    """
    return {
        'mse': compute_mse(actual, predicted),
        'rmse': compute_rmse(actual, predicted),
        'mae': compute_mae(actual, predicted),
        'r2': compute_r2_score(actual, predicted)
    }


def compute_confusion_matrix(actual: List[bool], predicted: List[bool]) -> Tuple[int, int, int, int]:
    """
    Compute confusion matrix for binary classification
    
    Args:
        actual: Actual labels
        predicted: Predicted labels
    
    Returns:
        (TP, TN, FP, FN) tuple
    """
    actual = np.array(actual, dtype=bool)
    predicted = np.array(predicted, dtype=bool)
    
    tp = np.sum((actual == True) & (predicted == True))
    tn = np.sum((actual == False) & (predicted == False))
    fp = np.sum((actual == False) & (predicted == True))
    fn = np.sum((actual == True) & (predicted == False))
    
    return int(tp), int(tn), int(fp), int(fn)


def compute_classification_metrics(actual: List[bool], predicted: List[bool]) -> Dict[str, float]:
    """
    Compute classification metrics
    
    Args:
        actual: Actual labels
        predicted: Predicted labels
    
    Returns:
        Dictionary of metrics
    """
    tp, tn, fp, fn = compute_confusion_matrix(actual, predicted)
    
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    accuracy = (tp + tn) / (tp + tn + fp + fn) if (tp + tn + fp + fn) > 0 else 0.0
    
    return {
        'precision': precision,
        'recall': recall,
        'f1_score': f1_score,
        'accuracy': accuracy,
        'true_positives': tp,
        'true_negatives': tn,
        'false_positives': fp,
        'false_negatives': fn
    }
