"""
Start Spark Jobs
Launches both batch and streaming Spark analytics
"""

import sys
from pathlib import Path
import argparse

sys.path.append(str(Path(__file__).parent.parent))

from spark.spark_batch_analysis import main as batch_analysis
from spark.spark_streaming_analysis import main as streaming_analysis


def main():
    parser = argparse.ArgumentParser(description="Start Spark analytics jobs")
    parser.add_argument(
        '--mode',
        choices=['batch', 'streaming', 'both'],
        default='both',
        help='Analytics mode to run'
    )
    
    args = parser.parse_args()
    
    if args.mode in ['batch', 'both']:
        print("Starting Spark Batch Analysis...")
        try:
            batch_analysis()
        except Exception as e:
            print(f"Batch analysis error: {e}")
    
    if args.mode in ['streaming', 'both']:
        print("Starting Spark Streaming Analysis...")
        try:
            streaming_analysis()
        except Exception as e:
            print(f"Streaming analysis error: {e}")


if __name__ == "__main__":
    main()
