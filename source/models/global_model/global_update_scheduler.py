"""
Global Model Update Scheduler
Periodically triggers global model aggregation
"""

import time
import schedule
import logging
from datetime import datetime
from pathlib import Path
import sys
import json

sys.path.append(str(Path(__file__).parent.parent.parent))

from models.global_model.global_model import GlobalModel
from models.global_model.aggregator import ModelAggregator


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class GlobalUpdateScheduler:
    """
    Schedules periodic global model updates
    """
    
    def __init__(self, update_interval_minutes=30, storage_path=None):
        """
        Initialize scheduler
        
        Args:
            update_interval_minutes: Minutes between global updates
            storage_path: Path to store global model
        """
        self.update_interval = update_interval_minutes
        self.global_model = GlobalModel()
        self.aggregator = ModelAggregator(aggregation_strategy='fedavg')
        
        if storage_path is None:
            storage_path = Path(__file__).parent / "global_model_weights.pkl"
        self.storage_path = Path(storage_path)
        
        self.pending_updates = []
        self.last_update_time = None
        
        logger.info(f"Global update scheduler initialized")
        logger.info(f"Update interval: {update_interval_minutes} minutes")
    
    def receive_local_update(self, device_id, model_weights, sample_count, metadata=None):
        """
        Receive a local model update
        
        Args:
            device_id: Device identifier
            model_weights: Model weights from local device
            sample_count: Number of samples used for training
            metadata: Optional additional metadata
        """
        update = {
            'device_id': device_id,
            'weights': model_weights,
            'sample_count': sample_count,
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {}
        }
        
        self.pending_updates.append(update)
        logger.info(f"Received update from {device_id}. Pending updates: {len(self.pending_updates)}")
    
    def perform_aggregation(self):
        """
        Perform global model aggregation
        """
        if not self.pending_updates:
            logger.info("No pending updates. Skipping aggregation.")
            return
        
        logger.info("=" * 60)
        logger.info(f"Starting global model aggregation at {datetime.now()}")
        logger.info(f"Pending updates: {len(self.pending_updates)}")
        
        # Aggregate updates
        aggregated_weights, metadata = self.aggregator.aggregate(self.pending_updates)
        
        if aggregated_weights:
            # Update global model
            aggregation_meta = self.global_model.aggregate_updates(
                self.pending_updates,
                aggregation_strategy='fedavg'
            )
            
            # Save global model
            self.global_model.save(self.storage_path)
            
            # Clear pending updates
            self.pending_updates = []
            self.last_update_time = datetime.now()
            
            logger.info(f"✓ Global model updated and saved to {self.storage_path}")
            logger.info(f"  Aggregation round: #{len(self.global_model.aggregation_history)}")
            logger.info(f"  Next update in {self.update_interval} minutes")
        else:
            logger.error("Aggregation failed")
        
        logger.info("=" * 60)
    
    def get_global_model_weights(self):
        """
        Get current global model weights
        
        Returns:
            Global model weights dictionary
        """
        return self.global_model.get_global_weights()
    
    def get_status(self):
        """
        Get scheduler status
        
        Returns:
            Status dictionary
        """
        return {
            'pending_updates': len(self.pending_updates),
            'last_update': self.last_update_time.isoformat() if self.last_update_time else None,
            'aggregation_rounds': len(self.global_model.aggregation_history),
            'device_contributions': self.global_model.device_contributions,
            'next_update_in_minutes': self.update_interval
        }
    
    def start(self):
        """
        Start the scheduler
        """
        logger.info("Starting global update scheduler...")
        
        # Schedule periodic aggregation
        schedule.every(self.update_interval).minutes.do(self.perform_aggregation)
        
        # Also perform aggregation immediately if there are pending updates
        if self.pending_updates:
            self.perform_aggregation()
        
        logger.info(f"✓ Scheduler started. Running every {self.update_interval} minutes")
        
        # Run scheduler loop
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")
    
    def run_once(self):
        """
        Run aggregation once (for testing)
        """
        logger.info("Running one-time aggregation...")
        self.perform_aggregation()


def main():
    """
    Main execution function
    """
    # Load configuration
    config_path = Path(__file__).parent.parent.parent / "config" / "scheduler_config.json"
    
    if config_path.exists():
        with open(config_path, 'r') as f:
            config = json.load(f)
        update_interval = config.get('global_update_interval_minutes', 30)
    else:
        update_interval = 30
    
    # Create and start scheduler
    scheduler = GlobalUpdateScheduler(update_interval_minutes=update_interval)
    scheduler.start()


if __name__ == "__main__":
    main()
