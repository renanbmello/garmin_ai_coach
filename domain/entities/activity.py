from datetime import datetime
from typing import Optional, List

class Activity:
    def __init__(
        self,
        id: int,
        start_time: datetime,
        duration: float,
        distance: float,
        average_speed: float,
        calories: float,
        activity_type: str,
        activity_name: Optional[str] = None,
        heart_rate_avg: Optional[float] = None,
        heart_rate_max: Optional[float] = None,
        heart_rate_zones: Optional[dict] = None,
        elevation_gain: Optional[float] = None,
        cadence_avg: Optional[float] = None,
        cadence_max: Optional[float] = None,
        splits: List[dict] = None,
        training_effect: Optional[float] = None,
        vo2_max: Optional[float] = None,
        recovery_time: Optional[int] = None,
        temperature: Optional[float] = None,
        feels_like: Optional[float] = None,
        humidity: Optional[float] = None,
        stride_length: Optional[float] = None,
        vertical_oscillation: Optional[float] = None,
        ground_contact_time: Optional[float] = None,
        vertical_ratio: Optional[float] = None,
        power_avg: Optional[float] = None,
        power_max: Optional[float] = None,
        training_effect_label: Optional[str] = None,
        training_effect_message: Optional[str] = None,
        anaerobic_effect: Optional[float] = None,
        intensity_minutes: Optional[dict] = None,
        steps: Optional[int] = None,
        avg_stress: Optional[int] = None,
        max_stress: Optional[int] = None,
        training_load: Optional[float] = None,
        training_status: Optional[str] = None,
        fitness_trend: Optional[dict] = None,
        performance_condition: Optional[int] = None,
        has_splits: bool = False,
        elapsed_duration: Optional[float] = None,
        moving_duration: Optional[float] = None,
        elevation_loss: Optional[float] = None,
        min_elevation: Optional[float] = None,
        max_elevation: Optional[float] = None,
        max_speed: Optional[float] = None
    ):
        self.id = id
        self.start_time = start_time
        self.duration = duration
        self.distance = distance
        self.average_speed = average_speed
        self.calories = calories
        self.activity_type = activity_type
        self.activity_name = activity_name
        self.heart_rate_avg = heart_rate_avg
        self.heart_rate_max = heart_rate_max
        self.heart_rate_zones = heart_rate_zones
        self.elevation_gain = elevation_gain
        self.cadence_avg = cadence_avg
        self.cadence_max = cadence_max
        self.splits = splits or []
        self.training_effect = training_effect
        self.vo2_max = vo2_max
        self.recovery_time = recovery_time
        self.temperature = temperature
        self.feels_like = feels_like
        self.humidity = humidity
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
        self.steps = steps
        self.avg_stress = avg_stress
        self.max_stress = max_stress
        self.training_load = training_load
        self.training_status = training_status
        self.fitness_trend = fitness_trend
        self.performance_condition = performance_condition
        self.has_splits = has_splits
        self.elapsed_duration = elapsed_duration
        self.moving_duration = moving_duration
        self.elevation_loss = elevation_loss
        self.min_elevation = min_elevation
        self.max_elevation = max_elevation
        self.max_speed = max_speed

    @property
    def pace(self) -> float:
        """
        Calculate average pace in minutes per kilometer
        Returns pace as minutes (including decimal for seconds)
        """
        if self.distance <= 0 or self.duration <= 0:
            return 0
            
        distance_km = self.distance / 1000
        duration_minutes = self.duration / 60
        
        return duration_minutes / distance_km
    
    @property
    def pace_formatted(self) -> str:
        """
        Returns pace in format 'MM:SS min/km'
        """
        pace = self.pace
        if pace <= 0:
            return "00:00 min/km"
            
        minutes = int(pace)
        seconds = int((pace - minutes) * 60)
        
        return f"{minutes:02d}:{seconds:02d} min/km"

    def dict(self):
        """Convert activity to dictionary with all attributes, including calculated ones"""
        base_dict = {
            'id': self.id,
            'activity_name': self.activity_name,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'duration': self.duration,
            'distance': self.distance,
            'average_speed': self.average_speed,
            'max_speed': self.max_speed,
            'heart_rate_avg': self.heart_rate_avg,
            'heart_rate_max': self.heart_rate_max,
            'calories': self.calories,
            'elevation_gain': self.elevation_gain,
            'elevation_loss': self.elevation_loss,
            'min_elevation': self.min_elevation,
            'max_elevation': self.max_elevation,
            'activity_type': self.activity_type,
            'cadence_avg': self.cadence_avg,
            'cadence_max': self.cadence_max,
            'training_effect': self.training_effect,
            'training_effect_label': self.training_effect_label,
            'training_effect_message': self.training_effect_message,
            'anaerobic_effect': self.anaerobic_effect,
            'vo2_max': self.vo2_max,
            'power_avg': self.power_avg,
            'power_max': self.power_max,
            'stride_length': self.stride_length,
            'ground_contact_time': self.ground_contact_time,
            'vertical_oscillation': self.vertical_oscillation,
            'vertical_ratio': self.vertical_ratio,
            'intensity_minutes': self.intensity_minutes,
            'steps': self.steps,
            'splits': self.splits,
            'moving_duration': self.moving_duration,
            'pace': self.pace,
            'pace_formatted': self.pace_formatted
        }
        return {k: v for k, v in base_dict.items() if v is not None}
