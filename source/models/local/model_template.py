"""
Neural Network Model Template for Local Device Training
Lightweight feedforward neural network for IoT sensor data
"""

import numpy as np
import pickle
from pathlib import Path
from datetime import datetime


class LocalNeuralNetwork:
    """
    Feedforward Neural Network for device-specific training
    """
    
    def __init__(self, input_size=4, hidden_sizes=[16, 8], output_size=4, learning_rate=0.01):
        """
        Initialize the neural network
        
        Args:
            input_size: Number of input features (default 4: temp, humidity, light, voltage)
            hidden_sizes: List of hidden layer sizes
            output_size: Number of output features
            learning_rate: Learning rate for gradient descent
        """
        self.input_size = input_size
        self.hidden_sizes = hidden_sizes
        self.output_size = output_size
        self.learning_rate = learning_rate
        
        # Initialize weights and biases
        self.weights = []
        self.biases = []
        
        # Input to first hidden layer
        layer_sizes = [input_size] + hidden_sizes + [output_size]
        
        for i in range(len(layer_sizes) - 1):
            # Xavier initialization
            limit = np.sqrt(6 / (layer_sizes[i] + layer_sizes[i + 1]))
            w = np.random.uniform(-limit, limit, (layer_sizes[i], layer_sizes[i + 1]))
            b = np.zeros((1, layer_sizes[i + 1]))
            
            self.weights.append(w)
            self.biases.append(b)
        
        # Training history
        self.training_history = {
            'losses': [],
            'timestamps': [],
            'update_count': 0
        }
    
    def sigmoid(self, x):
        """Sigmoid activation function"""
        return 1 / (1 + np.exp(-np.clip(x, -500, 500)))
    
    def sigmoid_derivative(self, x):
        """Derivative of sigmoid"""
        s = self.sigmoid(x)
        return s * (1 - s)
    
    def relu(self, x):
        """ReLU activation function"""
        return np.maximum(0, x)
    
    def relu_derivative(self, x):
        """Derivative of ReLU"""
        return (x > 0).astype(float)
    
    def forward(self, X):
        """
        Forward propagation
        
        Args:
            X: Input data (n_samples, input_size)
        
        Returns:
            Output predictions and intermediate activations
        """
        activations = [X]
        z_values = []
        
        for i in range(len(self.weights)):
            z = np.dot(activations[-1], self.weights[i]) + self.biases[i]
            z_values.append(z)
            
            # Use ReLU for hidden layers, sigmoid for output
            if i < len(self.weights) - 1:
                a = self.relu(z)
            else:
                a = self.sigmoid(z)
            
            activations.append(a)
        
        return activations, z_values
    
    def backward(self, X, y, activations, z_values):
        """
        Backward propagation
        
        Args:
            X: Input data
            y: Target values
            activations: Activations from forward pass
            z_values: Pre-activation values
        
        Returns:
            Gradients for weights and biases
        """
        m = X.shape[0]  # Number of samples
        
        weight_gradients = []
        bias_gradients = []
        
        # Output layer error
        delta = activations[-1] - y
        
        # Backpropagate through layers
        for i in range(len(self.weights) - 1, -1, -1):
            # Compute gradients
            dW = np.dot(activations[i].T, delta) / m
            db = np.sum(delta, axis=0, keepdims=True) / m
            
            weight_gradients.insert(0, dW)
            bias_gradients.insert(0, db)
            
            # Propagate error to previous layer
            if i > 0:
                delta = np.dot(delta, self.weights[i].T) * self.relu_derivative(z_values[i - 1])
        
        return weight_gradients, bias_gradients
    
    def train_step(self, X, y):
        """
        Perform one training step
        
        Args:
            X: Input data (n_samples, input_size)
            y: Target values (n_samples, output_size)
        
        Returns:
            Loss value
        """
        # Ensure inputs are numpy arrays
        X = np.array(X)
        y = np.array(y)
        
        # Reshape if needed
        if len(X.shape) == 1:
            X = X.reshape(1, -1)
        if len(y.shape) == 1:
            y = y.reshape(1, -1)
        
        # Forward pass
        activations, z_values = self.forward(X)
        
        # Compute loss (MSE)
        loss = np.mean((activations[-1] - y) ** 2)
        
        # Backward pass
        weight_gradients, bias_gradients = self.backward(X, y, activations, z_values)
        
        # Update weights and biases
        for i in range(len(self.weights)):
            self.weights[i] -= self.learning_rate * weight_gradients[i]
            self.biases[i] -= self.learning_rate * bias_gradients[i]
        
        # Record training history
        self.training_history['losses'].append(loss)
        self.training_history['timestamps'].append(datetime.now().isoformat())
        self.training_history['update_count'] += 1
        
        return loss
    
    def predict(self, X):
        """
        Make predictions
        
        Args:
            X: Input data
        
        Returns:
            Predictions
        """
        X = np.array(X)
        if len(X.shape) == 1:
            X = X.reshape(1, -1)
        
        activations, _ = self.forward(X)
        return activations[-1]
    
    def get_weights(self):
        """
        Get current weights and biases
        
        Returns:
            Dictionary containing weights, biases, and metadata
        """
        return {
            'weights': [w.tolist() for w in self.weights],
            'biases': [b.tolist() for b in self.biases],
            'architecture': {
                'input_size': self.input_size,
                'hidden_sizes': self.hidden_sizes,
                'output_size': self.output_size
            },
            'training_info': {
                'learning_rate': self.learning_rate,
                'update_count': self.training_history['update_count'],
                'last_loss': self.training_history['losses'][-1] if self.training_history['losses'] else None
            },
            'timestamp': datetime.now().isoformat()
        }
    
    def set_weights(self, weights_dict):
        """
        Set weights and biases from dictionary
        
        Args:
            weights_dict: Dictionary containing weights and biases
        """
        self.weights = [np.array(w) for w in weights_dict['weights']]
        self.biases = [np.array(b) for b in weights_dict['biases']]
    
    def save(self, filepath):
        """
        Save model to file
        
        Args:
            filepath: Path to save the model
        """
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        model_data = {
            'weights': self.weights,
            'biases': self.biases,
            'input_size': self.input_size,
            'hidden_sizes': self.hidden_sizes,
            'output_size': self.output_size,
            'learning_rate': self.learning_rate,
            'training_history': self.training_history
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
    
    @classmethod
    def load(cls, filepath):
        """
        Load model from file
        
        Args:
            filepath: Path to load the model from
        
        Returns:
            Loaded model instance
        """
        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)
        
        # Create model with same architecture
        model = cls(
            input_size=model_data['input_size'],
            hidden_sizes=model_data['hidden_sizes'],
            output_size=model_data['output_size'],
            learning_rate=model_data['learning_rate']
        )
        
        # Set weights and history
        model.weights = model_data['weights']
        model.biases = model_data['biases']
        model.training_history = model_data['training_history']
        
        return model


def create_training_data(sensor_reading, next_reading=None):
    """
    Create training data from sensor readings
    
    Args:
        sensor_reading: Current sensor reading dict
        next_reading: Next sensor reading (for supervised learning)
    
    Returns:
        X (input), y (target)
    """
    # Extract features
    X = np.array([
        sensor_reading['temperature'],
        sensor_reading['humidity'],
        sensor_reading['light'],
        sensor_reading['voltage']
    ])
    
    # For autoencoder-style training (reconstruct input)
    if next_reading is None:
        y = X.copy()
    else:
        # Predict next reading
        y = np.array([
            next_reading['temperature'],
            next_reading['humidity'],
            next_reading['light'],
            next_reading['voltage']
        ])
    
    return X, y
