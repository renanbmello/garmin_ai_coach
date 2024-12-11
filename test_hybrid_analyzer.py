import asyncio
from datetime import datetime, timedelta
from domain.entities.activity import Activity
from application.services.hybrid_analyzer import HybridAnalyzer
from application.services.ml_analyzer import MLAnalyzer
from application.services.llm_analyzer import LLMAnalyzer

def create_mock_activities():
    """Cria uma lista de atividades simuladas para teste"""
    activities = []
    base_date = datetime.now() - timedelta(days=10)
    
    for i in range(10):
        activity = Activity(
            id=i,
            start_time=base_date + timedelta(days=i),
            duration=3600.0,  # 1 hora
            distance=10000.0,  # 10km
            average_speed=2.8,  # m/s
            calories=750.0,
            activity_type="running",
            activity_name=f"Corrida {i+1}",
            heart_rate_avg=150 + (i % 3) * 5,
            heart_rate_max=180 + (i % 3) * 5,
            cadence_avg=170 + (i % 3) * 2,
            cadence_max=180 + (i % 3) * 2,
            training_effect=3.5 + (i % 3) * 0.2,
            vo2_max=50 + (i % 3),
            power_avg=250 + (i % 3) * 10,
            power_max=300 + (i % 3) * 10,
            elevation_gain=100 + (i % 3) * 20,
            elevation_loss=100 + (i % 3) * 20,
            training_effect_label="Improving",
            training_effect_message="Good aerobic benefit",
            anaerobic_effect=2.0 + (i % 3) * 0.3
        )
        activities.append(activity)
    
    return activities

class MockMLAnalyzer(MLAnalyzer):
    def __init__(self):
        pass
    
    def analyze_patterns(self, activities):
        return {
            "training_patterns": [0, 1, 0, 2, 1, 0, 1, 2, 0, 1],
            "unusual_activities": [3, 7],
            "cluster_summary": {
                "cluster_0": 4,
                "cluster_1": 4,
                "cluster_2": 2
            },
            "improvement_opportunities": [
                "Aumentar consistência nos treinos longos",
                "Melhorar recuperação entre sessões intensas",
                "Variar mais os tipos de treino"
            ]
        }

class MockLLMAnalyzer(LLMAnalyzer):
    def __init__(self):
        pass
    
    async def analyze_activities(self, activities, ml_context=None):
        return {
            "analysis": """
            Suas últimas 10 atividades mostram uma progressão consistente na intensidade 
            e volume dos treinos. Há uma tendência positiva no pace médio e boa 
            distribuição das zonas de frequência cardíaca.
            """,
            "key_findings": [
                "Melhora de 5% no pace médio",
                "Boa distribuição de intensidade",
                "Recuperação adequada entre sessões"
            ]
        }

async def test_hybrid_analysis():
    # Criar analisadores mock
    ml_analyzer = MockMLAnalyzer()
    llm_analyzer = MockLLMAnalyzer()
    
    # Criar o analisador híbrido
    hybrid_analyzer = HybridAnalyzer(ml_analyzer, llm_analyzer)
    
    # Criar atividades simuladas
    activities = create_mock_activities()
    
    # Executar análise
    analysis = await hybrid_analyzer.analyze_activities(activities)
    
    # Imprimir resultado formatado
    import json
    print(json.dumps(analysis, indent=2, default=str))

if __name__ == "__main__":
    asyncio.run(test_hybrid_analysis()) 