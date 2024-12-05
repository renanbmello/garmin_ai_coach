from functools import lru_cache
import json
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
from typing import List

load_dotenv()
logger = logging.getLogger(__name__)

@lru_cache()
def get_garmin_connector():
    return GarminConnector()

class GarminConnector:
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GarminConnector, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
            
        self.email = os.getenv("GARMIN_EMAIL")
        self.password = os.getenv("GARMIN_PASSWORD")
        self.client = None
        self._last_login = None
        self._activities_cache = {}
        self._details_cache = {}
        self._auth_lock = asyncio.Lock()
        self._initialized = True

        if not self.email or not self.password:
            raise ValueError("GARMIN_EMAIL and GARMIN_PASSWORD must be set")

    async def connect(self) -> None:
        """Connect to Garmin with retry logic and cache"""
        async with self._auth_lock:  
            if (self._last_login and 
                datetime.now() - self._last_login < timedelta(minutes=30) and 
                self.client):
                return

            retry_delay = 5
            max_retries = 3

            for attempt in range(max_retries):
                try:
                    if not self.client:
                        self.client = Garmin(self.email, self.password)
                    
                    if attempt > 0:  
                        await asyncio.sleep(retry_delay * (2 ** attempt))
                    
                    self.client.login()
                    self._last_login = datetime.now()
                    logger.info("Connected to Garmin")
                    return
                    
                except GarminConnectTooManyRequestsError:
                    if attempt == max_retries - 1:
                        raise
                    logger.warning(f"Too many requests, attempt {attempt + 1}/{max_retries}")
                    continue
                    
                except Exception as e:
                    logger.error(f"Error connecting to Garmin: {str(e)}")
                    raise

    def _convert_to_activity(self, activity_data: dict) -> Activity:
        """Convert Garmin activity data to Activity object"""
        try:
            start_time_str = activity_data.get('startTimeLocal', activity_data.get('start_time'))
            if start_time_str:
                start_time = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
            else:
                start_time = None

            return Activity(
                id=activity_data.get('activityId'),
                activity_name=activity_data.get('activityName'),
                start_time=start_time,
                duration=activity_data.get('duration', 0),
                moving_duration=activity_data.get('movingDuration'),
                distance=activity_data.get('distance', 0),
                average_speed=activity_data.get('averageSpeed', 0),
                max_speed=activity_data.get('maxSpeed'),
                heart_rate_avg=activity_data.get('averageHR'),
                heart_rate_max=activity_data.get('maxHR'),
                calories=activity_data.get('calories', 0),
                elevation_gain=activity_data.get('elevationGain'),
                elevation_loss=activity_data.get('elevationLoss'),
                min_elevation=activity_data.get('minElevation'),
                max_elevation=activity_data.get('maxElevation'),
                activity_type=activity_data.get('activityType', {}).get('typeKey', '').lower(),
                cadence_avg=activity_data.get('averageRunningCadenceInStepsPerMinute'),
                cadence_max=activity_data.get('maxRunningCadenceInStepsPerMinute'),
                training_effect=activity_data.get('aerobicTrainingEffect'),
                training_effect_label=activity_data.get('trainingEffectLabel'),
                training_effect_message=activity_data.get('aerobicTrainingEffectMessage'),
                anaerobic_effect=activity_data.get('anaerobicTrainingEffect'),
                vo2_max=activity_data.get('vO2MaxValue'),
                power_avg=activity_data.get('avgPower'),
                power_max=activity_data.get('maxPower'),
                stride_length=activity_data.get('avgStrideLength'),
                ground_contact_time=activity_data.get('avgGroundContactTime'),
                vertical_oscillation=activity_data.get('avgVerticalOscillation'),
                vertical_ratio=activity_data.get('avgVerticalRatio'),
                intensity_minutes={
                    'moderate': activity_data.get('moderateIntensityMinutes', 0),
                    'vigorous': activity_data.get('vigorousIntensityMinutes', 0)
                },
                steps=activity_data.get('steps'),
                splits=self._process_splits(activity_data)
            )
        except Exception as e:
            logger.error(f"Error converting activity data: {str(e)}")
            return None

    def _process_splits(self, activity_data: dict) -> list:
        """Process splits data from activity"""
        splits = []
        if 'splitSummaries' in activity_data:
            for split in activity_data['splitSummaries']:
                if split.get('splitType') == 'RWD_RUN':
                    splits.append({
                        'distance': split.get('distance', 0),
                        'duration': split.get('duration', 0),
                        'pace': split.get('averageSpeed', 0),
                        'elevation_gain': split.get('totalAscent', 0),
                        'max_speed': split.get('maxSpeed', 0)
                    })
        return splits

    async def get_latest_activity(self) -> Activity:
        """Get latest activity"""
        await self.connect()
        activities = self.client.get_activities(0, 1)
        if activities:
            return self._convert_to_activity(activities[0])
        return None

    async def get_activities(self, limit: int = 10) -> List[Activity]:
        """Get activities and convert them to Activity objects"""
        try:
            await self.connect()
            activities_data = self.client.get_activities(0, limit)
            
            activities = []
            for activity_data in activities_data:
                activity = self._convert_to_activity(activity_data)
                if activity:
                    activities.append(activity)
            
            return activities
        except Exception as e:
            logger.error(f"Error fetching activities: {str(e)}")
            raise

    async def get_weekly_activities(self) -> List[Activity]:
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

    async def get_activity_details(self, activity_id: int) -> dict:
        """Get activity details with caching"""
        try:
            await self.connect()
            
            cache_key = f"details_{activity_id}"
            if cache_key in self._details_cache:
                cache_time, cached_data = self._details_cache[cache_key]
                if datetime.now() - cache_time < timedelta(minutes=30):
                    return self._convert_to_activity(cached_data)

            activity_data = self.client.get_activity_details(activity_id)
            activity = self._convert_to_activity(activity_data)
            
            if activity:
                self._details_cache[cache_key] = (datetime.now(), activity_data)
            
            return activity
            
        except Exception as e:
            logger.error(f"Error getting activity details: {str(e)}")
            return None
