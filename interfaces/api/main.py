from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from infrastructure.garmin.garmin_connector import GarminConnector

app = FastAPI(title="Garmin AI Coach")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

garmin_connector = GarminConnector()

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

