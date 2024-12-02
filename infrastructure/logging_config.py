import logging
import sys
from datetime import datetime

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(f"logs/garmin_ai_coach_{datetime.now().strftime('%Y-%m-%d')}.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )

    logging.getLogger("garminconnect").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
