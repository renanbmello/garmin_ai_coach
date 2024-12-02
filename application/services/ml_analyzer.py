from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from typing import List, Dict, Any
import numpy as np
from domain.entities.activity import Activity

class MLAnalyzer:
    def __init__(self):
        self.scaler = StandardScaler()
        self.clustering_model = KMeans(n_clusters=5)
        
    def analyze_patterns(self, activities: List[Activity]) -> Dict[str, Any]:
        """Identifica padrões nos treinos usando ML"""
        features = self._extract_features(activities)
        scaled_features = self.scaler.fit_transform(features)
        
        training_patterns = self.clustering_model.fit_predict(scaled_features).tolist()
        
        return {
            "training_patterns": training_patterns,
            "unusual_activities": self._detect_anomalies(scaled_features),
            "improvement_opportunities": self._identify_improvement_areas(scaled_features),
            "cluster_summary": self._get_cluster_summary(training_patterns)
        }

    def _extract_features(self, activities: List[Activity]) -> List[List[float]]:
        """Extrai características das atividades para análise"""
        features = []
        for activity in activities:
            feature_vector = [
                float(activity.duration) if activity.duration else 0.0,
                float(activity.distance) if activity.distance else 0.0,
                float(activity.heart_rate_avg) if activity.heart_rate_avg else 0.0,
            ]
            features.append(feature_vector)
        return features

    def _detect_anomalies(self, scaled_features: List[List[float]]) -> List[int]:
        """Detect anomalies in training data"""
        return []

    def _identify_improvement_areas(self, scaled_features: List[List[float]]) -> List[str]:
        """Identify areas for improvement in training"""
        return [
            "Mantenha a consistência nos treinos",
            "Considere aumentar gradualmente a intensidade"
        ]

    def _get_cluster_summary(self, patterns: List[int]) -> Dict[str, int]:
        """Returns a summary of the cluster distribution"""
        summary = {}
        for i in range(self.clustering_model.n_clusters):
            summary[f"cluster_{i}"] = patterns.count(i)
        return summary