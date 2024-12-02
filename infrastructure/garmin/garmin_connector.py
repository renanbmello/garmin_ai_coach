import os
from dotenv import load_dotenv
from datetime import datetime
import asyncio
import logging
from garminconnect import (
    Garmin,
    GarminConnectAuthenticationError,
    GarminConnectConnectionError,
    GarminConnectTooManyRequestsError
)

load_dotenv()
logger = logging.getLogger(__name__)

class GarminConnector:
    MAX_RETRIES = 3
    RETRY_DELAY = 1

    def __init__(self):
        self.email = os.getenv("GARMIN_EMAIL")
        self.password = os.getenv("GARMIN_PASSWORD")
        self.client = None

        if not self.email or not self.password:
            raise ValueError("GARMIN_EMAIL and GARMIN_PASSWORD must be set")

    async def connect(self) -> None:
        """Connect to Garmin and login"""
        try:
            self.client = Garmin(self.email, self.password)
            self.client.login()
            logger.info("Connected to Garmin")
        except GarminConnectAuthenticationError:
            logger.error(f"Error connecting to Garmin: {str(e)}")
            raise
        except GarminConnectTooManyRequestsError:
            wait_time = (attempt + 1) * self.RETRY_DELAY
            logger.error(f"Too many requests to Garmin, retrying in {wait_time} seconds")
            await asyncio.sleep(wait_time)
            raise
        except GarminConnectionError as e:
            if attempt == self.MAX_RETRIES - 1:
                logger.error("Max retries reached, failed to connect to Garmin")
                raise
            wait_time = (attempt + 1) * self.RETRY_DELAY
            logger.warning(f"Connection error to Garmin, retrying in {wait_time} seconds")
            await asyncio.sleep(wait_time)
            raise
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
