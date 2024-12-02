import logging
from datetime import datetime
import os

def setup_logging():
    """Configure logging for the application"""
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(f"logs/garmin_ai_coach_{datetime.now().strftime('%Y-%m-%d')}.log"),
            logging.StreamHandler()
        ]
    )

    logging.getLogger("garminconnect").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
