import os
from dotenv import load_dotenv
from garminconnect import Garmin
from datetime import datetime

load_dotenv()

class GarminConnector:
    def __init__(self):
        self.email = os.getenv("GARMIN_EMAIL")
        self.password = os.getenv("GARMIN_PASSWORD")
        self.client = None

    async def connect(self):
        if not self.client:
            self.client = Garmin(self.email, self.password)
            self.client.login()
            print("Connected to Garmin")

    async def get_latest_activity(self):
        await self.connect()
        activities = self.client.get_activities(0, 1)
        return activities[0] if activities else None 

    async def get_activity_details(self, activity_id: str):
        await self.connect()
        return  self.client.get_activity_details(activity_id)
