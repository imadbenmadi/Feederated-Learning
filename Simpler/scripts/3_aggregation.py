"""
Component 3: Federated Aggregation
Team: IMED, AMIR

Aggregates local models into a global model using FedAvg
"""

import numpy as np
from pathlib import Path
import json
import pickle
from sklearn.neural_network import MLPRegressor


def load_config():
    """Load configuration"""
    config_path = Path(__file__).parent.parent / "config" / "settings.json"
    with open(config_path, 'r') as f:
        return json.load(f)


def aggregate_models():
    """Aggregate local models using FedAvg"""
    config = load_config()
    
    # Paths
    local_dir = Path(__file__).parent.parent / "models" / "local"
    global_dir = Path(__file__).parent.parent / "models" / "global"
    global_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print("FEDERATED AGGREGATION - FedAvg Algorithm")
    print("=" * 60)
    
    # Load all local models
    model_files = list(local_dir.glob("*.pkl"))
    print(f"\nFound {len(model_files)} local models")
    
    if len(model_files) < config['aggregation']['min_devices']:
        print(f"[ERROR] Need at least {config['aggregation']['min_devices']} models")
        return None
    
    local_models = []
    total_samples = 0
    
    print("\nLoading local models...")
    for model_file in model_files:
        with open(model_file, 'rb') as f:
            model_data = pickle.load(f)
            local_models.append(model_data)
            total_samples += model_data['num_samples']
            device_name = model_file.stem
            print(f"  {device_name}: {model_data['num_samples']} samples, Test R²={model_data['test_score']:.4f}")
    
    print(f"\nTotal samples across all devices: {total_samples}")
    
    # FedAvg: Weight each model by its number of samples
    print("\nAggregating weights using FedAvg...")
    
    # Get weights from first model as template
    first_model = local_models[0]['model']
    aggregated_coefs = [np.zeros_like(coef) for coef in first_model.coefs_]
    aggregated_intercepts = [np.zeros_like(intercept) for intercept in first_model.intercepts_]
    
    # Weighted average
    for model_data in local_models:
        weight = model_data['num_samples'] / total_samples
        model = model_data['model']
        
        for i in range(len(aggregated_coefs)):
            aggregated_coefs[i] += weight * model.coefs_[i]
            aggregated_intercepts[i] += weight * model.intercepts_[i]
    
    # Create global model
    hidden_layers = tuple(config['training']['hidden_layers'])
    global_model = MLPRegressor(
        hidden_layer_sizes=hidden_layers,
        max_iter=1,  # Already trained
        random_state=42
    )
    
    # Initialize with dummy data
    X_dummy = np.random.rand(10, 3)
    y_dummy = np.random.rand(10)
    global_model.fit(X_dummy, y_dummy)
    
    # Replace weights with aggregated ones
    global_model.coefs_ = aggregated_coefs
    global_model.intercepts_ = aggregated_intercepts
    
    # Calculate metadata
    avg_test_score = np.mean([m['test_score'] for m in local_models])
    
    # Save global model
    global_model_data = {
        'model': global_model,
        'num_devices': len(local_models),
        'total_samples': total_samples,
        'avg_test_score': avg_test_score,
        'aggregation_strategy': config['aggregation']['strategy']
    }
    
    global_file = global_dir / "global_model.pkl"
    with open(global_file, 'wb') as f:
        pickle.dump(global_model_data, f)
    
    print(f"\n[SUCCESS] Global model created")
    print(f"Participating devices: {len(local_models)}")
    print(f"Average test R²: {avg_test_score:.4f}")
    print(f"Saved to: {global_file}")
    
    print("\n" + "=" * 60)
    print("AGGREGATION COMPLETE")
    print("=" * 60)
    
    return global_model_data


if __name__ == "__main__":
    print()
    result = aggregate_models()
    if result:
        print("\nGlobal model ready!")
        print("Next step: Run 4_analytics.py")
