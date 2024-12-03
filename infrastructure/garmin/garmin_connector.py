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
        """Get activity details"""
        try:    
            activity = await self.get_activity_details(activity_id)

            print("Available activity details: ", json.dumps(activity, indent=2))

            splits = []
            if 'splitSummaries' in activity:
                for split in activity['splitSummaries']:
                    if split['splitType'] == 'RWD_RUN':  # Pegando apenas os splits de corrida
                        splits.append({
                            'distance': split.get('distance', 0),
                            'duration': split.get('duration', 0),
                            'pace': split.get('averageSpeed', 0),
                            'elevation_gain': split.get('totalAscent', 0),
                            'max_speed': split.get('maxSpeed', 0)
                    })
            return {
            'splits': splits,
            'cadence_avg': activity.get('averageRunningCadenceInStepsPerMinute'),
            'cadence_max': activity.get('maxRunningCadenceInStepsPerMinute'),
            'training_effect': activity.get('aerobicTrainingEffect'),
            'anaerobic_effect': activity.get('anaerobicTrainingEffect'),
            'vo2_max': activity.get('vO2MaxValue'),
            'training_effect_label': activity.get('trainingEffectLabel'),
            'training_effect_message': activity.get('aerobicTrainingEffectMessage'),
            'stride_length': activity.get('avgStrideLength'),
            'vertical_oscillation': activity.get('avgVerticalOscillation'),
            'ground_contact_time': activity.get('avgGroundContactTime'),
            'vertical_ratio': activity.get('avgVerticalRatio'),
            'power_avg': activity.get('avgPower'),
            'power_max': activity.get('maxPower'),
            'elevation_min': activity.get('minElevation'),
            'elevation_max': activity.get('maxElevation'),
            'intensity_minutes': {
                'moderate': activity.get('moderateIntensityMinutes', 0),
                'vigorous': activity.get('vigorousIntensityMinutes', 0)
            }
        }
        except Exception as e:
            logger.error(f"Error getting activity details: {str(e)}")
            return {}

    async def get_activities(self, limit: int = 20) -> list[Activity]:
        """Get activities with specified limit"""
        await self.connect()
        
        try:
            raw_activities = self.client.get_activities(0, limit)
            # print("Raw activities: ", json.dumps(raw_activities, indent=2))
            
            activities = []
            for activity_data in raw_activities:
                if activity_data.get('activityType', {}).get('typeKey', '').lower() == "running":
                    details = await self.get_activity_details(activity_data['activityId'])
                    
                    activity = Activity(
                    id=activity_data['activityId'],
                    start_time=datetime.fromisoformat(activity_data['startTimeLocal'].replace('Z', '+00:00')),
                    duration=activity_data.get('duration', 0),
                    distance=activity_data.get('distance', 0),
                    heart_rate_avg=activity_data.get('averageHR'),
                    heart_rate_max=activity_data.get('maxHR'),
                    heart_rate_zone=None,
                    pace=activity_data.get('averageSpeed', 0),
                    calories=activity_data.get('calories', 0),
                    elevation_gain=activity_data.get('elevationGain'),
                    activity_type=activity_data.get('activityType', {}).get('typeKey', '').lower(),
                    cadence_avg=details.get('cadence_avg'),
                    cadence_max=details.get('cadence_max'),
                    splits=details.get('splits', []),
                    training_effect=details.get('training_effect'),
                    vo2_max=details.get('vo2_max'),
                    stride_length=details.get('stride_length'),
                    vertical_oscillation=details.get('vertical_oscillation'),
                    ground_contact_time=details.get('ground_contact_time'),
                    vertical_ratio=details.get('vertical_ratio'),
                    power_avg=details.get('power_avg'),
                    power_max=details.get('power_max'),
                    training_effect_label=details.get('training_effect_label'),
                    training_effect_message=details.get('training_effect_message'),
                    anaerobic_effect=details.get('anaerobic_effect'),
                    intensity_minutes=details.get('intensity_minutes')
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
