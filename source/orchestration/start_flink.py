"""
Start Flink Job
Launches the Flink streaming job for local model training
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from flink.flink_job import main as start_flink


if __name__ == "__main__":
    print("Starting Flink Job...")
    start_flink()
