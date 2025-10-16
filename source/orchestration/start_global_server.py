"""
Start Global Model Server
Launches the FastAPI server for federated learning
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from global_server.app import main as start_server


if __name__ == "__main__":
    print("Starting Global Model Server...")
    start_server()
