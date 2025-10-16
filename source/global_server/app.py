"""
Global Model Aggregation Server
FastAPI server for receiving local model updates and serving global model
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, List, Optional
import uvicorn
from datetime import datetime
from pathlib import Path
import sys
import logging
import json

sys.path.append(str(Path(__file__).parent.parent))

from models.global_model.global_model import GlobalModel
from models.global_model.aggregator import ModelAggregator


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Pydantic models for API
class LocalModelUpdate(BaseModel):
    device_id: str
    weights: Dict
    sample_count: int
    timestamp: str
    metadata: Optional[Dict] = None


class GlobalModelResponse(BaseModel):
    weights: Dict
    timestamp: str
    aggregation_round: int
    total_devices: int


# Initialize FastAPI app
app = FastAPI(
    title="IoT Global Model Server",
    description="Federated learning aggregation server for IoT devices",
    version="1.0.0"
)


# Global state
global_model = GlobalModel()
aggregator = ModelAggregator(aggregation_strategy='fedavg')
pending_updates = []
aggregation_config = {
    'auto_aggregate_threshold': 5,  # Aggregate when N updates received
    'manual_mode': False
}


@app.get("/")
async def root():
    """
    Root endpoint
    """
    return {
        "service": "IoT Global Model Server",
        "status": "running",
        "version": "1.0.0"
    }


@app.post("/api/local-update")
async def receive_local_update(update: LocalModelUpdate):
    """
    Receive a local model update from a device
    """
    try:
        # Store update
        update_dict = {
            'device_id': update.device_id,
            'weights': update.weights,
            'sample_count': update.sample_count,
            'timestamp': update.timestamp,
            'metadata': update.metadata or {}
        }
        
        pending_updates.append(update_dict)
        
        logger.info(f"Received update from {update.device_id}. Pending: {len(pending_updates)}")
        
        # Auto-aggregate if threshold reached
        if not aggregation_config['manual_mode'] and \
           len(pending_updates) >= aggregation_config['auto_aggregate_threshold']:
            logger.info("Auto-aggregation threshold reached. Triggering aggregation...")
            result = await trigger_aggregation()
            return {
                "status": "received_and_aggregated",
                "device_id": update.device_id,
                "pending_updates": 0,
                "aggregation_result": result
            }
        
        return {
            "status": "received",
            "device_id": update.device_id,
            "pending_updates": len(pending_updates)
        }
    
    except Exception as e:
        logger.error(f"Error receiving update: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/aggregate")
async def trigger_aggregation():
    """
    Manually trigger global model aggregation
    """
    global pending_updates
    
    if not pending_updates:
        return {
            "status": "no_updates",
            "message": "No pending updates to aggregate"
        }
    
    try:
        logger.info(f"Triggering aggregation for {len(pending_updates)} updates")
        
        # Perform aggregation
        result = global_model.aggregate_updates(
            pending_updates,
            aggregation_strategy='fedavg'
        )
        
        if result:
            # Save global model
            model_path = Path(__file__).parent.parent / "models" / "global" / "global_model_weights.pkl"
            global_model.save(model_path)
            
            # Clear pending updates
            num_aggregated = len(pending_updates)
            pending_updates = []
            
            logger.info(f"✓ Aggregation complete. Aggregated {num_aggregated} updates")
            
            return {
                "status": "success",
                "aggregated_updates": num_aggregated,
                "aggregation_round": len(global_model.aggregation_history),
                "timestamp": result['timestamp'],
                "device_ids": result['device_ids']
            }
        else:
            raise Exception("Aggregation failed")
    
    except Exception as e:
        logger.error(f"Error during aggregation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/global-model")
async def get_global_model():
    """
    Get the current global model
    """
    try:
        weights = global_model.get_global_weights()
        summary = global_model.get_summary()
        
        return {
            "weights": weights,
            "summary": summary,
            "aggregation_rounds": len(global_model.aggregation_history),
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error getting global model: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/status")
async def get_status():
    """
    Get server status and statistics
    """
    return {
        "status": "running",
        "pending_updates": len(pending_updates),
        "aggregation_rounds": len(global_model.aggregation_history),
        "unique_devices": len(global_model.device_contributions),
        "device_contributions": global_model.device_contributions,
        "aggregation_config": aggregation_config,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/history")
async def get_aggregation_history():
    """
    Get aggregation history
    """
    return {
        "aggregation_history": global_model.aggregation_history,
        "total_rounds": len(global_model.aggregation_history)
    }


@app.post("/api/config")
async def update_config(config: Dict):
    """
    Update server configuration
    """
    try:
        global aggregation_config
        aggregation_config.update(config)
        
        logger.info(f"Configuration updated: {aggregation_config}")
        
        return {
            "status": "updated",
            "config": aggregation_config
        }
    
    except Exception as e:
        logger.error(f"Error updating config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def main():
    """
    Start the server
    """
    print("=" * 60)
    print("IoT Global Model Server")
    print("=" * 60)
    print("Starting FastAPI server...")
    print("API Documentation: http://localhost:8000/docs")
    print("=" * 60)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )


if __name__ == "__main__":
    main()
