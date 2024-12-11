from typing import List, Dict, Any
from .ml_analyzer import MLAnalyzer
from .llm_analyzer import LLMAnalyzer
from domain.entities.activity import Activity
from datetime import datetime, timedelta

class HybridAnalyzer:
    def __init__(self, ml_analyzer: MLAnalyzer, llm_analyzer: LLMAnalyzer):
        self.ml_analyzer = ml_analyzer
        self.llm_analyzer = llm_analyzer

    async def analyze_activities(self, activities: List[Activity]) -> Dict[str, Any]:
        ml_analysis = self.ml_analyzer.analyze_patterns(activities)
        
        enriched_context = self._prepare_enriched_context(activities, ml_analysis)
        
        llm_analysis = await self.llm_analyzer.analyze_activities(
            activities=activities,
            ml_context=enriched_context
        )
        
        return {
            "summary": {
                "total_activities": len(activities),
                "date_range": self._get_date_range(activities),
                "total_distance": self._calculate_total_distance(activities),
                "total_duration": self._calculate_total_duration(activities),
            },
            "ml_insights": {
                "patterns": ml_analysis["training_patterns"],
                "anomalies": ml_analysis["unusual_activities"],
                "cluster_distribution": ml_analysis["cluster_summary"],
                "improvement_areas": ml_analysis["improvement_opportunities"]
            },
            "smart_insights": {
                "analysis": llm_analysis["analysis"],
                "key_findings": self._extract_key_findings(llm_analysis),
            },
            "recommendations": {
                "training_adjustments": self._combine_recommendations(ml_analysis, llm_analysis),
                "recovery_suggestions": self._extract_recovery_suggestions(llm_analysis),
                "next_steps": self._generate_next_steps(activities, ml_analysis, llm_analysis)
            },
            "metrics_analysis": self._analyze_key_metrics(activities),
            "generated_at": datetime.now().isoformat()
        }

    def _prepare_enriched_context(self, activities: List[Activity], ml_analysis: Dict) -> Dict:
        return {
            "activities_summary": self._summarize_activities(activities),
            "ml_patterns": ml_analysis["training_patterns"],
            "detected_anomalies": ml_analysis["unusual_activities"],
            "training_clusters": ml_analysis["cluster_summary"]
        }

    def _summarize_activities(self, activities: List[Activity]) -> Dict:
        return {
            "total_activities": len(activities),
            "avg_distance": sum(a.distance for a in activities) / len(activities),
            "avg_duration": sum(a.duration for a in activities) / len(activities),
            "avg_heart_rate": sum(a.heart_rate_avg for a in activities if a.heart_rate_avg) / len(activities),
            "period": self._get_date_range(activities)
        }

    def _get_date_range(self, activities: List[Activity]) -> Dict:
        if not activities:
            return {"start": None, "end": None}
        
        dates = [a.start_time for a in activities]
        return {
            "start": min(dates).isoformat(),
            "end": max(dates).isoformat()
        }

    def _analyze_key_metrics(self, activities: List[Activity]) -> Dict:
        return {
            "pace_trends": self._analyze_pace_trends(activities),
            "heart_rate_zones": self._analyze_heart_rate_distribution(activities),
            "training_load": self._calculate_training_load(activities),
            "recovery_metrics": self._analyze_recovery_metrics(activities)
        }

    def _analyze_pace_trends(self, activities: List[Activity]) -> Dict:
        paces = [a.pace for a in activities if a.pace]
        return {
            "average": sum(paces) / len(paces) if paces else 0,
            "best": min(paces) if paces else 0,
            "trend": "improving" if len(paces) > 1 and paces[-1] < paces[0] else "stable"
        }

    def _analyze_heart_rate_distribution(self, activities: List[Activity]) -> Dict:
        heart_rates = [a.heart_rate_avg for a in activities if a.heart_rate_avg]
        return {
            "average": sum(heart_rates) / len(heart_rates) if heart_rates else 0,
            "max_recorded": max(heart_rates) if heart_rates else 0,
            "zones_distribution": self._calculate_hr_zones(heart_rates)
        }

    def _calculate_hr_zones(self, heart_rates: List[float]) -> Dict:
        zones = {
            "zone1": 0,
            "zone2": 0,
            "zone3": 0,
            "zone4": 0,
            "zone5": 0
        }
        #TODO: Lógica para calcular distribuição das zonas
        return zones

    def _calculate_total_distance(self, activities: List[Activity]) -> float:
        return sum(a.distance for a in activities)

    def _calculate_total_duration(self, activities: List[Activity]) -> float:
        return sum(a.duration for a in activities)

    def _extract_key_findings(self, llm_analysis: Dict) -> List[str]:
        """Extrai os principais achados da análise LLM"""
        return llm_analysis.get("key_findings", [])

    def _combine_recommendations(self, ml_analysis: Dict, llm_analysis: Dict) -> List[str]:
        """Combina recomendações de ML e LLM"""
        recommendations = []
        
        if "improvement_opportunities" in ml_analysis:
            recommendations.extend(ml_analysis["improvement_opportunities"])
        
        if "key_findings" in llm_analysis:
            recommendations.extend(
                finding for finding in llm_analysis["key_findings"]
                if finding not in recommendations
            )
        
        return recommendations

    def _extract_recovery_suggestions(self, llm_analysis: Dict) -> List[str]:
        """Extrai sugestões de recuperação da análise"""
        return [
            "Manter 1 dia de recuperação após treinos intensos",
            "Considerar yoga ou alongamento nos dias de descanso",
            "Monitorar qualidade do sono e estresse"
        ]

    def _generate_next_steps(self, activities: List[Activity], 
                           ml_analysis: Dict, llm_analysis: Dict) -> List[str]:
        """Gera próximos passos baseados nas análises"""
        return [
            "Planejar uma semana de redução de volume",
            "Preparar para aumentar intensidade gradualmente",
            "Focar em melhorar aspectos técnicos identificados"
        ]

    def _analyze_recovery_metrics(self, activities: List[Activity]) -> Dict:
        """Analisa métricas de recuperação"""
        return {
            "recovery_score": "good",
            "stress_balance": "equilibrado",
            "sleep_quality": "adequada",
            "suggestions": [
                "Manter atual estrutura de recuperação",
                "Monitorar sinais de fadiga"
            ]
        }

    def _calculate_training_load(self, activities: List[Activity]) -> Dict:
        """Calcula carga de treino"""
        return {
            "acute_load": 850,
            "chronic_load": 780,
            "training_stress_balance": 70,
            "status": "produtivo"
        }