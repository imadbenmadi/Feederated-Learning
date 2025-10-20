"""
Component 5: Visualization
Team: YUSIF, AMIR

Creates visualizations and dashboards
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import json
import pickle


def load_config():
    """Load configuration"""
    config_path = Path(__file__).parent.parent / "config" / "settings.json"
    with open(config_path, 'r') as f:
        return json.load(f)


def create_visualizations():
    """Generate visualizations"""
    config = load_config()
    
    print("=" * 60)
    print("VISUALIZATION - Dashboards & Charts")
    print("=" * 60)
    
    # Output directory
    output_dir = Path(__file__).parent.parent / "outputs" / "visualizations"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load data
    data_file = Path(__file__).parent.parent / "data" / "processed" / "processed_iot_data.csv"
    df = pd.read_csv(data_file)
    
    print(f"\nLoaded {len(df)} records from {df['device_id'].nunique()} devices")
    
    # Load analytics report
    report_file = Path(__file__).parent.parent / "outputs" / "analytics" / "analytics_report.json"
    with open(report_file, 'r') as f:
        analytics = json.load(f)
    
    # Create figure with subplots
    fig = plt.figure(figsize=(16, 12))
    
    # 1. Temperature Distribution
    ax1 = plt.subplot(3, 3, 1)
    df['temperature'].hist(bins=50, ax=ax1, color='steelblue', edgecolor='black')
    ax1.set_title('Temperature Distribution', fontsize=12, fontweight='bold')
    ax1.set_xlabel('Temperature (°C)')
    ax1.set_ylabel('Frequency')
    ax1.grid(True, alpha=0.3)
    
    # 2. Humidity Distribution
    ax2 = plt.subplot(3, 3, 2)
    df['humidity'].hist(bins=50, ax=ax2, color='lightgreen', edgecolor='black')
    ax2.set_title('Humidity Distribution', fontsize=12, fontweight='bold')
    ax2.set_xlabel('Humidity (%)')
    ax2.set_ylabel('Frequency')
    ax2.grid(True, alpha=0.3)
    
    # 3. Light Distribution
    ax3 = plt.subplot(3, 3, 3)
    df['light'].hist(bins=50, ax=ax3, color='orange', edgecolor='black')
    ax3.set_title('Light Distribution', fontsize=12, fontweight='bold')
    ax3.set_xlabel('Light (Lux)')
    ax3.set_ylabel('Frequency')
    ax3.grid(True, alpha=0.3)
    
    # 4. Voltage Distribution
    ax4 = plt.subplot(3, 3, 4)
    df['voltage'].hist(bins=50, ax=ax4, color='red', edgecolor='black', alpha=0.7)
    ax4.set_title('Voltage Distribution', fontsize=12, fontweight='bold')
    ax4.set_xlabel('Voltage (V)')
    ax4.set_ylabel('Frequency')
    ax4.grid(True, alpha=0.3)
    
    # 5. Records per Device (Top 20)
    ax5 = plt.subplot(3, 3, 5)
    device_counts = df['device_id'].value_counts().head(20)
    device_counts.plot(kind='bar', ax=ax5, color='purple', edgecolor='black')
    ax5.set_title('Records per Device (Top 20)', fontsize=12, fontweight='bold')
    ax5.set_xlabel('Device ID')
    ax5.set_ylabel('Number of Records')
    ax5.tick_params(axis='x', rotation=45, labelsize=8)
    ax5.grid(True, alpha=0.3, axis='y')
    
    # 6. Temperature vs Humidity Scatter
    ax6 = plt.subplot(3, 3, 6)
    sample = df.sample(n=min(1000, len(df)))
    ax6.scatter(sample['temperature'], sample['humidity'], alpha=0.5, s=10, color='teal')
    ax6.set_title('Temperature vs Humidity', fontsize=12, fontweight='bold')
    ax6.set_xlabel('Temperature (°C)')
    ax6.set_ylabel('Humidity (%)')
    ax6.grid(True, alpha=0.3)
    
    # 7. Model Performance
    ax7 = plt.subplot(3, 3, 7)
    local_dir = Path(__file__).parent.parent / "models" / "local"
    model_scores = []
    device_names = []
    
    for model_file in sorted(local_dir.glob("*.pkl"))[:20]:
        with open(model_file, 'rb') as f:
            model_data = pickle.load(f)
            model_scores.append(model_data['test_score'])
            device_names.append(model_file.stem)
    
    ax7.barh(range(len(model_scores)), model_scores, color='darkgreen', edgecolor='black')
    ax7.set_title('Model Test R² Score (Top 20 Devices)', fontsize=12, fontweight='bold')
    ax7.set_xlabel('R² Score')
    ax7.set_ylabel('Device')
    ax7.set_yticks(range(len(device_names)))
    ax7.set_yticklabels(device_names, fontsize=7)
    ax7.grid(True, alpha=0.3, axis='x')
    ax7.set_xlim([0, 1])
    
    # 8. Sensor Statistics Summary
    ax8 = plt.subplot(3, 3, 8)
    ax8.axis('off')
    summary_text = f"""
    DATASET SUMMARY
    
    Total Records: {len(df):,}
    Devices: {df['device_id'].nunique()}
    
    TEMPERATURE
    Min: {df['temperature'].min():.2f}°C
    Max: {df['temperature'].max():.2f}°C
    Mean: {df['temperature'].mean():.2f}°C
    
    HUMIDITY
    Min: {df['humidity'].min():.2f}%
    Max: {df['humidity'].max():.2f}%
    Mean: {df['humidity'].mean():.2f}%
    
    ANOMALIES DETECTED
    Count: {analytics['anomalies']}
    Percentage: {analytics['anomalies']/len(df)*100:.2f}%
    """
    ax8.text(0.1, 0.5, summary_text, fontsize=10, family='monospace',
             verticalalignment='center', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    # 9. Global Model Info
    ax9 = plt.subplot(3, 3, 9)
    ax9.axis('off')
    
    global_file = Path(__file__).parent.parent / "models" / "global" / "global_model.pkl"
    if global_file.exists():
        with open(global_file, 'rb') as f:
            global_data = pickle.load(f)
        
        model_text = f"""
        GLOBAL MODEL
        
        Strategy: FedAvg
        Devices: {global_data['num_devices']}
        Total Samples: {global_data['total_samples']:,}
        Avg Test R²: {global_data['avg_test_score']:.4f}
        
        TRAINING CONFIG
        Hidden Layers: {config['training']['hidden_layers']}
        Epochs: {config['training']['epochs']}
        Learning Rate: {config['training']['learning_rate']}
        """
    else:
        model_text = "Global model not found.\nRun 3_aggregation.py first."
    
    ax9.text(0.1, 0.5, model_text, fontsize=10, family='monospace',
             verticalalignment='center', bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))
    
    plt.suptitle('IoT Federated Learning Pipeline - Analytics Dashboard', 
                 fontsize=16, fontweight='bold', y=0.995)
    plt.tight_layout()
    
    # Save figure
    dashboard_file = output_dir / "dashboard.png"
    plt.savefig(dashboard_file, dpi=150, bbox_inches='tight')
    print(f"\n[SUCCESS] Dashboard saved: {dashboard_file}")
    
    # Show plot
    plt.show()
    
    print("\n" + "=" * 60)
    print("VISUALIZATION COMPLETE")
    print("=" * 60)
    print(f"\nOutputs saved in: {output_dir}")
    
    return dashboard_file


if __name__ == "__main__":
    print()
    result = create_visualizations()
    print("\nAll visualizations created!")
    print("Pipeline complete!")
