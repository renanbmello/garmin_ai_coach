from typing import List
from sqlalchemy.orm import Session
from infrastructure.repositories.activity_repository import ActivityRepository
from infrastructure.garmin.garmin_connector import GarminConnector
from domain.models.activity import Activity as ActivityModel

class DataInitializationService:
    def __init__(self, db: Session, activity_repository: ActivityRepository, garmin_connector: GarminConnector):
        self.db = db
        self.activity_repository = activity_repository
        self.garmin_connector = garmin_connector

    async def initialize_data(self, limit: int = 100):
        """Fetch activities from Garmin and save to database"""
        activities = await self.garmin_connector.get_activities(limit)
        
        db_activities = []
        for activity in activities:
            db_activity = ActivityModel(
                activity_id=str(activity.id),
                start_time=activity.start_time,
                duration=activity.duration,
                distance=activity.distance,
                heart_rate_avg=activity.heart_rate_avg,
                heart_rate_max=activity.heart_rate_max,
                calories=activity.calories,
                elevation_gain=activity.elevation_gain,
                activity_type=activity.activity_type
            )
            db_activities.append(db_activity)
        
        self.activity_repository.save_many(db_activities)
        return len(db_activities) 