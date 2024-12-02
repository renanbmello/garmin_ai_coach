import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import asyncio
import logging
from garminconnect import (
    Garmin,
    GarminConnectAuthenticationError,
    GarminConnectConnectionError,
    GarminConnectTooManyRequestsError
)
from domain.entities.activity import Activity

load_dotenv()
logger = logging.getLogger(__name__)

class GarminConnector:
    MAX_RETRIES = 5
    INITIAL_RETRY_DELAY = 5  

    def __init__(self):
        self.email = os.getenv("GARMIN_EMAIL")
        self.password = os.getenv("GARMIN_PASSWORD")
        self.client = None

        if not self.email or not self.password:
            raise ValueError("GARMIN_EMAIL and GARMIN_PASSWORD must be set")

    async def connect(self) -> None:
        """Connect to Garmin and login"""
        retry_delay = self.INITIAL_RETRY_DELAY
        for attempt in range(self.MAX_RETRIES):
            try:
                if not self.client:
                    self.client = Garmin(self.email, self.password)
                
                self.client.login()
                logger.info("Connected to Garmin")
                return
                
            except GarminConnectTooManyRequestsError:
                logger.warning(f"Too many requests to Garmin, waiting {retry_delay} seconds...")
                await asyncio.sleep(retry_delay)
                retry_delay *= 2  
                if attempt == self.MAX_RETRIES - 1:
                    raise
                continue
                
            except GarminConnectAuthenticationError as e:
                logger.error(f"Authentication error with Garmin: {str(e)}")
                raise
                
            except GarminConnectConnectionError as e:
                logger.warning(f"Connection error to Garmin, retrying in {retry_delay} seconds")
                await asyncio.sleep(retry_delay)
                retry_delay *= 2  
                if attempt == self.MAX_RETRIES - 1:
                    raise
                continue
                
            except Exception as e:
                logger.error(f"Unexpected error connecting to Garmin: {str(e)}")
                raise

    async def get_session_status(self) -> dict[str, any]:
        """Get the session status"""
        try:
            if not self.client:
                return {"status": "disconnected"}

            self.client.get_user_summary()
            return {
                "status": "connected",
                "email": self.email,
                "last_check": datetime.now().isoformat()
            }
        except Exception as e:
            return {"status": "expired"}

    async def get_latest_activity(self):
        await self.connect()
        activities = self.client.get_activities(0, 1)
        return activities[0] if activities else None 

    async def get_activity_details(self, activity_id: str):
        await self.connect()
        return  self.client.get_activity_details(activity_id)

    async def get_activities(self, limit: int = 20) -> list[Activity]:
        """Get activities with specified limit"""
        await self.connect()
        
        try:
            raw_activities = self.client.get_activities(0, limit)
            
            activities = []
            for raw in raw_activities:
                activity = Activity(
                    id=raw.get('activityId'),
                    start_time=datetime.fromisoformat(raw.get('startTimeLocal').replace('Z', '+00:00')),
                    duration=raw.get('duration', 0),  
                    distance=raw.get('distance', 0), 
                    heart_rate_avg=raw.get('averageHR'),  
                    heart_rate_max=raw.get('maxHR'),
                    heart_rate_zone=None,  
                    pace=raw.get('averageSpeed'),
                    calories=raw.get('calories'),
                    elevation_gain=raw.get('elevationGain'),
                    activity_type=raw.get('activityType', {}).get('typeKey', 'unknown')
                )
                activities.append(activity)
            
            return activities
        except Exception as e:
            logger.error(f"Error getting activities: {str(e)}")
            raise

    async def get_weekly_activities(self) -> list[Activity]:
        """Get activities from the last 7 days"""
        await self.connect()
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        try:
            activities = await self.get_activities(limit=20)
            
            weekly_activities = [
                activity for activity in activities
                if start_date <= activity.start_time <= end_date
            ]
            
            return weekly_activities
        except Exception as e:
            logger.error(f"Error getting weekly activities: {str(e)}")
            raise
