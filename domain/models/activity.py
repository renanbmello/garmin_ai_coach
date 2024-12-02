from sqlalchemy import Column, Integer, String, Float, DateTime
from infrastructure.database import Base

class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True)
    activity_id = Column(String, unique=True)
    start_time = Column(DateTime, nullable=False)
    duration = Column(Float, nullable=False)
    distance = Column(Float, nullable=False)
    heart_rate_avg = Column(Float)
    heart_rate_max = Column(Float)
    calories = Column(Float)
    elevation_gain = Column(Float)
    activity_type = Column(String)

    def __repr__(self):
        return f"<Activity(id={self.id}, type={self.activity_type}, date={self.start_time})>" 