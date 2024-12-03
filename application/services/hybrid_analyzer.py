from typing import List
from .ml_analyzer import MLAnalyzer
from .llm_analyzer import LLMAnalyzer
from domain.entities.activity import Activity

class HybridAnalyzer:
    def __init__(self, ml_analyzer: MLAnalyzer, llm_analyzer: LLMAnalyzer):
        self.ml_analyzer = ml_analyzer
        self.llm_analyzer = llm_analyzer

    async def analyze_activities(self, activities: List[Activity]) -> dict:
        ml_analysis = self.ml_analyzer.analyze_patterns(activities)
        
        context = {
            "activities": activities,
            "ml_insights": ml_analysis,
        }
        
        llm_analysis = await self.llm_analyzer.analyze_activities(
            activities=activities,
            ml_context=ml_analysis
        )
        
        return {
            "statistical_analysis": ml_analysis,
            "smart_insights": llm_analysis,
            "combined_recommendations": llm_analysis["recommendations"]
        } 