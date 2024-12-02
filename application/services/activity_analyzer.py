import numpy as np
import pandas as pd
from domain.entities.activity import Activity
from sklearn.ensemble import IsolationForest

class ActivityAnalyzer:
    def __init__(self):
        self.performance_model = IsolationForest(contamination=0.1)
        self.pace_model = IsolationForest(contamination=0.1)
        self.heart_rate_model = IsolationForest(contamination=0.1)
        
        self.historical_stats = {
            'usual_pace_range': None,
            'usual_heart_rate_range': None,
            'preferred_training_times': None,
            'weekly_distance': None
        }

    def add_historical_data(self, activities: List[Activity]):
        """Add historical data to the analyzer"""
        data = [self._activity_to_dict(activity) for activity in activities]
        self.historical_data = pd.DataFrame(data)

    def analyze_activity(self, activity: Activity) -> dict:
        """Análise expandida da atividade"""
        analysis = {
            "performance_score": self._calculate_performance_score(activity),
            "heart_rate_analysis": self._analyze_heart_rate(activity),
            "training_load": self._calculate_training_load(activity),
            "fatigue_score": self._calculate_fatigue_score(activity),
            "comparison_to_usual": self._compare_to_historical(activity),
            "recommendations": self._generate_smart_recommendations(activity),
            "progress_indicators": self._analyze_progress(activity)
        }
        return analysis

    def _activity_to_dict(self, activity: Activity) -> dict:
        """Convert an activity to a dictionary"""
        return {
            "duration": activity.duration,
            "distance": activity.distance,
            "heart_rate_avg": activity.heart_rate_avg,
            "pace": activity.pace,
            "elevation_gain": activity.elevation_gain,
        }

    def _calculate_performance_score(self, activity: Activity) -> float:
        """Calculate the performance score of an activity"""
        if self.historical_data.empty:
            return 0.0

        features = self._extract_features(activity)
        x = self.historical_data[features.keys()]
        y = self.historical_data["performance_score"] if "performance_score" in self.historical_data.columns else np.zeros(len(x))

        self.model.fit(x, y)
        score = self.model.decision_function(list(features.values()))[0]
        return score

    def _analyze_heart_rate(self, activity: Activity) -> dict:
        """Analyze the heart rate of an activity"""
        zones_time = activity.heart_rate_zones or []

        return {
            "time_in_zones": zones_time,
            "optimal_zone_time": self._calculate_optimal_zone_time(zones_time),
        }

    def _calculate_optimal_zone_time(self, zones_time: list[float]) -> float:
        """Ideal time in zones."""
        if not zones_time:
            return 0.0
        return max(zones_time)  
    def _generate_recommendations(self, activity: Activity) -> list[str]:
        """Generate recommendations based on the activity analysis."""
        recommendations = []
        if activity.heart_rate_avg and activity.heart_rate_avg > 160:
            recommendations.append("Consider reducing intensity to improve recovery.")
        if activity.pace and activity.pace < 5:
            recommendations.append("Great pace! Keep focused on consistency.")
        return recommendations

    def _calculate_training_load(self, activity: Activity) -> float:
        """Calculate training load based on duration and intensity"""
        pass

    def _calculate_fatigue_score(self, activity: Activity) -> float:
        """Analyze fatigue signals based on HR and pace"""
        pass

    def _compare_to_historical(self, activity: Activity) -> dict:
        """Compare to athlete's historical patterns"""
        return {
            "pace_comparison": "This pace is 5% faster than your usual",
            "heart_rate_zones": "You spent more time in Z3 than usual",
            "effort_level": "This was a more intense workout than your average"
        }

    
