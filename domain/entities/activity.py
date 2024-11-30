from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

@dataclass
class Activity:
    id: str
    start_time: datetime
    duration: float
    distance: float
    heart_rate_avg: Optional[float]
    heart_rate_max: Optional[float]
    heart_rate_zone: Optional[float]
    pace: Optional[float]
    calories: Optional[float]
    elevation_gain: Optional[float]
