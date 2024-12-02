from typing import List, Dict, Any
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest
import joblib
import os
from domain.models.activity import Activity
from infrastructure.repositories.activity_repository import ActivityRepository

class MLAnalyzer:
    def __init__(self, activity_repository: ActivityRepository):
        self.activity_repository = activity_repository
        self.scaler = StandardScaler()
        self.clustering_model = KMeans(n_clusters=5)
        self.anomaly_detector = IsolationForest(contamination=0.1)
        self.model_path = "models/"
        os.makedirs(self.model_path, exist_ok=True)

    def train_models(self):
        """Trains models with historical data"""
        activities = self.activity_repository.get_all()
        if not activities:
            raise ValueError("No activities found for training")

        features = self._extract_features(activities)
        
        scaled_features = self.scaler.fit_transform(features)
        
        self.clustering_model.fit(scaled_features)
        
        self.anomaly_detector.fit(scaled_features)
        
        self._save_models()
        
        return "Models trained successfully"

    def load_models(self):
        """Loads previously trained models"""
        try:
            self.scaler = joblib.load(f"{self.model_path}scaler.joblib")
            self.clustering_model = joblib.load(f"{self.model_path}clustering.joblib")
            self.anomaly_detector = joblib.load(f"{self.model_path}anomaly_detector.joblib")
            return True
        except FileNotFoundError:
            return False

    def _save_models(self):
        """Saves trained models"""
        joblib.dump(self.scaler, f"{self.model_path}scaler.joblib")
        joblib.dump(self.clustering_model, f"{self.model_path}clustering.joblib")
        joblib.dump(self.anomaly_detector, f"{self.model_path}anomaly_detector.joblib")

    def analyze_patterns(self, activities: List[Activity]) -> Dict[str, Any]:
        """Analyzes training patterns using trained models"""
        if not self.load_models():
            self.train_models()

        features = self._extract_features(activities)
        scaled_features = self.scaler.transform(features)
        
        clusters = self.clustering_model.predict(scaled_features)
        anomalies = self.anomaly_detector.predict(scaled_features)
        
        return {
            "training_patterns": clusters.tolist(),
            "unusual_activities": [i for i, is_anomaly in enumerate(anomalies) if is_anomaly == -1],
            "improvement_opportunities": self._identify_improvement_areas(scaled_features),
            "cluster_summary": self._get_cluster_summary(clusters)
        }

    def _extract_features(self, activities: List[Activity]) -> np.ndarray:
        """Extracts relevant features from activities"""
        features = []
        for activity in activities:
            feature_vector = [
                float(activity.duration or 0),
                float(activity.distance or 0),
                float(activity.heart_rate_avg or 0),
                float(activity.heart_rate_max or 0),
                float(activity.calories or 0),
                float(activity.elevation_gain or 0)
            ]
            features.append(feature_vector)
        return np.array(features)

    def _identify_improvement_areas(self, scaled_features: np.ndarray) -> List[str]:
        """Identifies areas for improvement based on training patterns"""
        # Basic implementation - TODO: can be expanded with more analysis
        return [
            "Keep consistency in training",
            "Consider gradually increasing intensity",
            "Vary activity types for a more comprehensive training"
        ]

    def _get_cluster_summary(self, clusters: np.ndarray) -> Dict[str, int]:
        """Returns a summary of the cluster distribution"""
        unique, counts = np.unique(clusters, return_counts=True)
        return {f"cluster_{int(cluster)}": int(count) for cluster, count in zip(unique, counts)}