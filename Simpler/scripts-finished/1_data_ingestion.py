"""
Component 1: Data Ingestion
Team: SU YOUNG, ROBERT

Downloads the Intel Lab IoT dataset
"""

import urllib.request
from pathlib import Path
import json


def load_config():
    """Load configuration"""
    config_path = Path(__file__).parent.parent / "config" / "settings.json"
    with open(config_path, 'r') as f:
        return json.load(f)


def download_dataset():
    """Download Intel Lab dataset"""
    config = load_config()
    url = config['dataset']['source_url']
    
    # Create output directory
    output_dir = Path(__file__).parent.parent / "data" / "raw"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "intel_lab_data.txt"
    
    print("=" * 60)
    print("DATA INGESTION - Intel Lab Dataset")
    print("=" * 60)
    print(f"\nDownloading from: {url}")
    print(f"Saving to: {output_file}")
    
    try:
        urllib.request.urlretrieve(url, output_file)
        
        # Count lines
        with open(output_file, 'r') as f:
            line_count = sum(1 for _ in f)
        
        print(f"\n[SUCCESS] Downloaded {line_count} records")
        print(f"File size: {output_file.stat().st_size / (1024*1024):.2f} MB")
        
        return output_file
        
    except Exception as e:
        print(f"\n[ERROR] Download failed: {e}")
        return None


if __name__ == "__main__":
    result = download_dataset()
    if result:
        print("\n" + "=" * 60)
        print("INGESTION COMPLETE")
        print("=" * 60)
        print("\nNext step: Run 1_preprocessing.py")
    else:
        print("\n[FAILED] Please check your internet connection")
