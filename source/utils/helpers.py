"""
Helper Utilities
Generic utility functions used across the project
"""

import json
import pickle
from pathlib import Path
from typing import Any, Dict
import hashlib


def load_json(filepath: str) -> Dict:
    """
    Load JSON file
    
    Args:
        filepath: Path to JSON file
    
    Returns:
        Dictionary from JSON
    """
    with open(filepath, 'r') as f:
        return json.load(f)


def save_json(data: Dict, filepath: str, indent: int = 2):
    """
    Save dictionary to JSON file
    
    Args:
        data: Dictionary to save
        filepath: Output file path
        indent: JSON indentation
    """
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=indent)


def load_pickle(filepath: str) -> Any:
    """
    Load pickled object
    
    Args:
        filepath: Path to pickle file
    
    Returns:
        Unpickled object
    """
    with open(filepath, 'rb') as f:
        return pickle.load(f)


def save_pickle(obj: Any, filepath: str):
    """
    Save object to pickle file
    
    Args:
        obj: Object to pickle
        filepath: Output file path
    """
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    with open(filepath, 'wb') as f:
        pickle.dump(obj, f)


def compute_file_hash(filepath: str, algorithm: str = 'sha256') -> str:
    """
    Compute hash of a file
    
    Args:
        filepath: Path to file
        algorithm: Hash algorithm (sha256, md5, etc.)
    
    Returns:
        Hexadecimal hash string
    """
    hasher = hashlib.new(algorithm)
    
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hasher.update(chunk)
    
    return hasher.hexdigest()


def ensure_directory(dirpath: str):
    """
    Ensure directory exists, create if not
    
    Args:
        dirpath: Directory path
    """
    Path(dirpath).mkdir(parents=True, exist_ok=True)


def get_project_root() -> Path:
    """
    Get project root directory
    
    Returns:
        Path to project root
    """
    return Path(__file__).parent.parent


def format_bytes(bytes_value: int) -> str:
    """
    Format bytes to human-readable string
    
    Args:
        bytes_value: Number of bytes
    
    Returns:
        Formatted string
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024.0
    
    return f"{bytes_value:.2f} PB"


def merge_dicts(dict1: Dict, dict2: Dict) -> Dict:
    """
    Recursively merge two dictionaries
    
    Args:
        dict1: First dictionary
        dict2: Second dictionary (takes precedence)
    
    Returns:
        Merged dictionary
    """
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = value
    
    return result
