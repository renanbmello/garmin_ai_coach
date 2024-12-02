from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from infrastructure.garmin.garmin_connector import GarminConnector
from .middleware import GarminSessionMiddleware
from application.services.auth_service import AuthenticationService
app = FastAPI(title="Garmin AI Coach")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

garmin_connector = GarminConnector()

app.add_middleware(GarminSessionMiddleware)

auth_service = AuthenticationService()

@app.get("/auth/status")
async def get_auth_status():
    """Get the authentication status"""
    try:
        connector = auth_service.connector
        status = await connector.get_session_status()
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/auth/refresh")
async def refresh_auth():
    """Refresh the authentication"""
    try:
        await auth_service.ensure_authentication()
        return {"status": "Authentication refreshed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def get_latest_activity():
    try:
        activity = await garmin_connector.get_latest_activity()
        return activity
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/latest-activity")
async def get_latest_activity():
    try:
        activity = await garmin_connector.get_latest_activity()
        return activity
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

