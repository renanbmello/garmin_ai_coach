from typing import Optional
import logging
from datetime import datetime, timedelta
from infrastructure.garmin.garmin_connector import GarminConnector

logger = logging.getLogger(__name__)

class AuthenticationService:
    def __init__(self):
        self._connector: Optional[GarminConnector] = None
        self._last_login: Optional[datetime] = None
        self._session_duration: timedelta = timedelta(hours=1)
        self._last_attempt: Optional[datetime] = None
        self._retry_cooldown: timedelta = timedelta(minutes=5)

    @property
    def connector(self) -> GarminConnector:
        if not self._connector:
            self._connector = GarminConnector()
        return self._connector

    def needs_refresh(self) -> bool:
        if not self._last_login:
            return True
        return datetime.now() - self._last_login > self._session_duration

    def can_retry(self) -> bool:
        if not self._last_attempt:
            return True
        return datetime.now() - self._last_attempt > self._retry_cooldown

    async def ensure_authentication(self):
        try:
            if self.needs_refresh():
                if not self.can_retry():
                    logger.warning("Too many login attempts. Waiting for cooldown...")
                    return
                
                self._last_attempt = datetime.now()
                await self.connector.connect()
                self._last_login = datetime.now()
                logger.info("Authenticated with Garmin")
                
        except Exception as e:
            logger.error(f"Error authenticating with Garmin: {str(e)}")
            raise e


