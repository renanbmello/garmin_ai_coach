from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from infrastructure.database import Base

class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True)
    activity_id = Column(String, unique=True)
    start_time = Column(DateTime, nullable=False)
    duration = Column(Float, nullable=False)
    distance = Column(Float, nullable=False)
    average_speed = Column(Float)
    max_speed = Column(Float)
    heart_rate_avg = Column(Float)
    heart_rate_max = Column(Float)
    calories = Column(Float)
    elevation_gain = Column(Float)
    elevation_loss = Column(Float)
    min_elevation = Column(Float)
    max_elevation = Column(Float)
    activity_type = Column(String)
    activity_name = Column(String)
    cadence_avg = Column(Float)
    cadence_max = Column(Float)
    splits = Column(JSON)
    training_effect = Column(Float)
    training_effect_label = Column(String)
    training_effect_message = Column(String)
    anaerobic_effect = Column(Float)
    vo2_max = Column(Float)
    power_avg = Column(Float)
    power_max = Column(Float)
    moving_duration = Column(Float)
    intensity_minutes = Column(JSON)
    steps = Column(Integer)
    pace = Column(Float)
    pace_formatted = Column(String)

    def __repr__(self):
        return f"<Activity(id={self.id}, type={self.activity_type}, date={self.start_time})>" 