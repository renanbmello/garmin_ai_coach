from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from infrastructure.garmin.garmin_connector import GarminConnector
from .middleware import GarminSessionMiddleware
from application.services.auth_service import AuthenticationService
from application.services.trend_analyzer import TrendAnalyzer
from application.services.ml_analyzer import MLAnalyzer
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

trend_analyzer = TrendAnalyzer()

ml_analyzer = MLAnalyzer()

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

@app.get("/analysis/weekly-summary")
async def get_weekly_summary():
    """Get weekly summary of workouts"""
    activities = await garmin_connector.get_weekly_activities()
    analysis = trend_analyzer.analyze_weekly_trends(activities)
    return analysis

@app.get("/analysis/training-patterns")
async def get_training_patterns():
    """Get training patterns identified"""
    activities = await garmin_connector.get_activities(limit=50)
    patterns = ml_analyzer.analyze_patterns(activities)
    return patterns

