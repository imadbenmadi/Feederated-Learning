"""
Dataset Download Script
Downloads the Intel Lab IoT sensor dataset for the pipeline
"""

import os
import urllib.request
import zipfile
from pathlib import Path


def download_intel_lab_data():
    """
    Downloads Intel Lab Data from the public repository
    """
    # Create raw data directory if it doesn't exist
    raw_data_dir = Path(__file__).parent / "raw"
    raw_data_dir.mkdir(parents=True, exist_ok=True)
    
    # Dataset URL (Intel Lab Data)
    url = "http://db.csail.mit.edu/labdata/data.txt"
    output_file = raw_data_dir / "intel_lab_data.txt"
    
    print(f"Downloading Intel Lab Data from {url}...")
    
    try:
        urllib.request.urlretrieve(url, output_file)
        print(f"✓ Dataset downloaded successfully to {output_file}")
        
        # Display basic info
        file_size = os.path.getsize(output_file)
        print(f"✓ File size: {file_size / (1024 * 1024):.2f} MB")
        
        # Count lines
        with open(output_file, 'r') as f:
            line_count = sum(1 for _ in f)
        print(f"✓ Total records: {line_count}")
        
        return output_file
        
    except Exception as e:
        print(f"✗ Error downloading dataset: {e}")
        return None


def convert_to_csv(input_file, output_file):
    """
    Converts the downloaded text file to CSV format
    """
    print(f"\nConverting {input_file} to CSV format...")
    
    try:
        with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
            # Write header
            outfile.write("date,time,epoch,device_id,temperature,humidity,light,voltage\n")
            
            # Process each line
            line_count = 0
            for line in infile:
                parts = line.strip().split()
                # Intel Lab data has ONLY 6 columns: date time epoch device_id temperature humidity light voltage
                # But actually it's: epoch device_id temperature humidity light voltage (6 columns)
                # We need to parse the actual epoch as both date and time
                if len(parts) >= 6:
                    # Add placeholder date/time columns based on epoch
                    # Format: date, time, epoch, device_id, temperature, humidity, light, voltage
                    # The parts are: epoch(0), device_id(1), temp(2), humidity(3), light(4), voltage(5)
                    epoch = parts[0]
                    device_id = parts[1]
                    temperature = parts[2]
                    humidity = parts[3]
                    light = parts[4]
                    voltage = parts[5]
                    
                    # Convert epoch to date/time (Intel Lab base: 2004-02-28)
                    from datetime import datetime, timedelta
                    try:
                        base_date = datetime(2004, 2, 28)
                        dt = base_date + timedelta(seconds=int(float(epoch)))
                        date_str = dt.strftime('%Y-%m-%d')
                        time_str = dt.strftime('%H:%M:%S')
                    except:
                        date_str = '2004-02-28'
                        time_str = '00:00:00'
                    
                    # Write CSV line
                    csv_line = f"{date_str},{time_str},{epoch},{device_id},{temperature},{humidity},{light},{voltage}\n"
                    outfile.write(csv_line)
                    line_count += 1
            
            print(f"✓ CSV file created: {output_file}")
            print(f"✓ Converted {line_count} data records")
        
        return output_file
        
    except Exception as e:
        print(f"✗ Error converting to CSV: {e}")
        return None


def main():
    """
    Main execution function
    """
    print("=" * 60)
    print("Intel Lab Data Download Script")
    print("=" * 60)
    
    # Download dataset
    downloaded_file = download_intel_lab_data()
    
    if downloaded_file:
        # Convert to CSV
        raw_data_dir = Path(__file__).parent / "raw"
        csv_file = raw_data_dir / "intel_lab_data.csv"
        convert_to_csv(downloaded_file, csv_file)
        
        print("\n" + "=" * 60)
        print("✓ Download complete!")
        print("=" * 60)
        print(f"Raw data location: {raw_data_dir}")
        print("\nNext step: Run preprocess_dataset.py to clean and prepare the data")
    else:
        print("\n✗ Download failed. Please check your internet connection and try again.")


if __name__ == "__main__":
    main()
