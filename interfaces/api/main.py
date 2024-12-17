from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from infrastructure.garmin.garmin_connector import get_garmin_connector, GarminConnector
from .middleware import GarminSessionMiddleware
from application.services.auth_service import AuthenticationService
from application.services.trend_analyzer import TrendAnalyzer
from application.services.ml_analyzer import MLAnalyzer
from application.services.llm_analyzer import LLMAnalyzer
from application.services.hybrid_analyzer import HybridAnalyzer
from sqlalchemy.orm import Session
from infrastructure.database import SessionLocal
from infrastructure.repositories.activity_repository import ActivityRepository
from application.services.data_initialization_service import DataInitializationService
from infrastructure.database_init import init_database
import logging
from datetime import datetime

# Inicializa o banco de dados na inicialização da aplicação
init_database()

app = FastAPI(title="Garmin AI Coach")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

garmin_connector = get_garmin_connector()

app.add_middleware(GarminSessionMiddleware)

auth_service = AuthenticationService()

trend_analyzer = TrendAnalyzer()

logger = logging.getLogger(__name__)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_activity_repository(db: Session = Depends(get_db)):
    return ActivityRepository(db)

def get_ml_analyzer(repository: ActivityRepository = Depends(get_activity_repository)):
    return MLAnalyzer(repository)

def get_llm_analyzer(repository: ActivityRepository = Depends(get_activity_repository)):
    return LLMAnalyzer(repository)

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

@app.get("/activities")
async def get_activities(
    limit: int = 50,
    garmin_connector: GarminConnector = Depends(get_garmin_connector)
):
    """Get activities"""
    try:
        activities = await garmin_connector.get_activities(limit=limit)
        running_activities = [
            activity.dict()
            for activity in activities
            if activity.activity_type.lower() == "running"
        ]
        return running_activities
    except Exception as e:
        logger.error(f"Error getting activities: {str(e)}")
        if "Too Many Requests" in str(e):
            raise HTTPException(
                status_code=429,
                detail="Too many requests to Garmin. Please try again in a few minutes."
            )
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/latest-activity")
async def get_latest_activity():
    """Get latest activity"""
    try:
        activity = await garmin_connector.get_latest_activity()
        if activity is None:
            raise HTTPException(status_code=404, detail="No activity found")
        return activity
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/activity-details/{activity_id}")
async def get_activity_details(
    activity_id: int,
    garmin_connector: GarminConnector = Depends(get_garmin_connector)
):
    try:
        details = await garmin_connector.get_activity_details(activity_id)
        if not details:
            raise HTTPException(status_code=404, detail="Activity not found")
        return details
    except Exception as e:
        logger.error(f"Error getting activity details: {str(e)}")
        if "Too Many Requests" in str(e):
            raise HTTPException(
                status_code=429,
                detail="Too many requests to Garmin. Please try again in a few minutes."
            )
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analysis/weekly-summary")
async def get_weekly_summary():
    """Get weekly summary of workouts"""
    activities = await garmin_connector.get_weekly_activities()
    analysis = trend_analyzer.analyze_weekly_trends(activities)
    return analysis

@app.get("/analysis/training-patterns")
async def get_training_patterns(
    ml_analyzer: MLAnalyzer = Depends(get_ml_analyzer)
):
    """Get training patterns identified"""
    activities = await garmin_connector.get_activities(limit=50)
    patterns = ml_analyzer.analyze_patterns(activities)
    return patterns

@app.post("/initialize-data")
async def initialize_data(
    limit: int = 100,
    db: Session = Depends(get_db),
    repository: ActivityRepository = Depends(get_activity_repository)
):
    """Initialize database with Garmin data"""
    garmin_connector = get_garmin_connector()
    service = DataInitializationService(db, repository, garmin_connector)
    
    try:
        count = await service.initialize_data(limit)
        return {"message": f"Successfully initialized {count} activities"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analysis/initial")
async def get_initial_analysis(
    ml_analyzer: MLAnalyzer = Depends(get_ml_analyzer),
    repository: ActivityRepository = Depends(get_activity_repository)
):
    """Perform initial analysis of stored data"""
    activities = repository.get_all()
    if not activities:
        raise HTTPException(status_code=404, detail="No activities found")
    
    try:
        analysis = ml_analyzer.analyze_patterns(activities)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analysis/smart")
async def smart_analysis(
    db: Session = Depends(get_db),
    garmin_connector: GarminConnector = Depends(get_garmin_connector)
):
    """Get smart analysis from GPT-4"""
    try:
        activities = await garmin_connector.get_activities(limit=10)
        llm_analyzer = LLMAnalyzer()
        analysis = await llm_analyzer.analyze_activities(activities)
        
        print("Smart Analysis Response:", analysis)  # Para debug
        return analysis
        
    except Exception as e:
        logger.error(f"Error in smart analysis: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail={"status": "error", "message": str(e)}
        )

@app.get("/analysis/hybrid")
async def get_hybrid_analysis(
    ml_analyzer: MLAnalyzer = Depends(get_ml_analyzer),
    llm_analyzer: LLMAnalyzer = Depends(get_llm_analyzer),
    repository: ActivityRepository = Depends(get_activity_repository)
):
    """Get combined ML and LLM analysis"""
    activities = repository.get_all()
    if not activities:
        raise HTTPException(status_code=404, detail="No activities found")
    
    hybrid_analyzer = HybridAnalyzer(ml_analyzer, llm_analyzer)
    analysis = await hybrid_analyzer.analyze_activities(activities)
    return analysis

@app.get("/analysis/preview")
async def preview_analysis(
    db: Session = Depends(get_db),
    garmin_connector: GarminConnector = Depends(get_garmin_connector)
):
    """Preview the analysis prompt without sending to GPT-4"""
    try:
        activities = await garmin_connector.get_activities(limit=10)
        print("activities")
        print(activities[0].dict())
        running_activities = [a for a in activities if a.activity_type.lower() == "running"]
        running_activities = running_activities[:10]
        
        llm_analyzer = LLMAnalyzer()
        context = llm_analyzer._prepare_activity_context(running_activities)
        
        system_message = """You are an experienced running coach specializing in training data analysis and periodization. 
        Focus on practical insights and detailed analysis of running metrics including pace, heart rate, cadence, 
        and training effect. Consider the relationship between these metrics and their impact on performance and recovery. This data is from Garmin device."""
        
        user_message = f"""
        Analyze the last {len(running_activities)} running activities and provide:
        
        1. Progress:
           - Pace evolution and consistency
           - Distance progression
           - Heart rate trends and zones
           - Cadence analysis
        
        2. Training Load:
           - Weekly volume and intensity
           - Training effect and recovery needs
           - VO2 Max trends
           - Signs of fatigue or overload
        
        3. Technical Analysis:
           - Pace distribution within runs
           - Cadence optimization
           - Heart rate response to pace changes
           - Impact of environmental factors
        
        4. Recommendations:
           - Volume/intensity adjustments
           - Recovery strategies
           - Technical improvements
           - Suggested next goals
        
        Data from running activities:
        {context}
        
        Please provide a detailed but practical analysis focusing on actionable insights.
        """
        analysis_send = {
            "system_message": system_message,
            "user_message": user_message,
            "context": context,  
            "metadata": {
                "activities_analyzed": len(running_activities),
                "date_range": {
                    "start": running_activities[-1].start_time.isoformat() if running_activities else None,
                    "end": running_activities[0].start_time.isoformat() if running_activities else None
                }
            }
        }
        print("analysis_send")
        print(analysis_send)
        return analysis_send
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

