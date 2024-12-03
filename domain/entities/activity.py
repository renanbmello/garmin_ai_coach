from datetime import datetime
from typing import Optional, List

class Activity:
    def __init__(
        self,
        id: int,
        start_time: datetime,
        duration: float,
        distance: float,
        heart_rate_avg: Optional[float],
        heart_rate_max: Optional[float],
        heart_rate_zone: Optional[str],
        pace: float,
        calories: float,
        elevation_gain: Optional[float],
        activity_type: str,
        cadence_avg: Optional[float] = None,
        cadence_max: Optional[float] = None,
        splits: List[dict] = None,
        training_effect: Optional[float] = None,
        vo2_max: Optional[float] = None,
        recovery_time: Optional[int] = None,
        temperature: Optional[float] = None,
        stride_length: Optional[float] = None,
        vertical_oscillation: Optional[float] = None,
        ground_contact_time: Optional[float] = None,
        vertical_ratio: Optional[float] = None,
        power_avg: Optional[float] = None,
        power_max: Optional[float] = None,
        training_effect_label: Optional[str] = None,
        training_effect_message: Optional[str] = None,
        anaerobic_effect: Optional[float] = None,
        intensity_minutes: Optional[dict] = None
    ):
        self.id = id
        self.start_time = start_time
        self.duration = duration
        self.distance = distance
        self.heart_rate_avg = heart_rate_avg
        self.heart_rate_max = heart_rate_max
        self.heart_rate_zone = heart_rate_zone
        self.pace = pace
        self.calories = calories
        self.elevation_gain = elevation_gain
        self.activity_type = activity_type
        self.cadence_avg = cadence_avg
        self.cadence_max = cadence_max
        self.splits = splits or []
        self.training_effect = training_effect
        self.vo2_max = vo2_max
        self.recovery_time = recovery_time
        self.temperature = temperature
        self.stride_length = stride_length
        self.vertical_oscillation = vertical_oscillation
        self.ground_contact_time = ground_contact_time
        self.vertical_ratio = vertical_ratio
        self.power_avg = power_avg
        self.power_max = power_max
        self.training_effect_label = training_effect_label
        self.training_effect_message = training_effect_message
        self.anaerobic_effect = anaerobic_effect
        self.intensity_minutes = intensity_minutes or {}
