from typing import List
import openai
import os
from domain.entities.activity import Activity

class LLMAnalyzer:
    def __init__(self, repository=None):
        self.repository = repository
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    async def analyze_activities(self, activities: List[Activity]) -> dict:
        running_activities = [a for a in activities if a.activity_type.lower() == "running"]
        running_activities = running_activities[:10]  

        context = self._prepare_activity_context(running_activities)
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system", 
                        "content": """You are an experienced running coach specializing in training data analysis and periodization. 
                        Focus on practical insights and detailed analysis of running metrics including pace, heart rate, cadence, 
                        and training effect. Consider the relationship between these metrics and their impact on performance and recovery."""
                    },
                    {
                        "role": "user", 
                        "content": f"""
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
                    }
                ]
            )
            
            return {
                "analysis": response.choices[0].message.content,
                "metadata": {
                    "model": "gpt-4",
                    "activities_analyzed": len(running_activities),
                    "date_range": {
                        "start": running_activities[-1].start_time.isoformat() if running_activities else None,
                        "end": running_activities[0].start_time.isoformat() if running_activities else None
                    }
                }
            }
        except Exception as e:
            return {
                "error": str(e),
                "status": "error",
                "activities_analyzed": len(running_activities)
            }

    def _calculate_pace(self, duration_seconds: float, distance_meters: float) -> str:
        """Calcula e formata o pace em min:sec/km"""
        if distance_meters <= 0:
            return "N/A"
        
        duration_minutes = duration_seconds / 60
        distance_km = distance_meters / 1000
        
        pace = duration_minutes / distance_km
        
        minutes = int(pace)
        seconds = int((pace - minutes) * 60)
        return f"{minutes}:{seconds:02d}/km"

    def _prepare_activity_context(self, activities: List[Activity]) -> str:
        if not activities:
            return "No activities found"
        
        return "\n".join([
            f"Running {idx+1} ({activity.start_time.strftime('%Y-%m-%d %H:%M')}):\n"
            f"- Duration: {activity.duration:.0f} minutes\n"
            f"- Distance: {(activity.distance / 1000):.2f} km\n"
            f"- Average Pace: {self._calculate_pace(activity.duration, activity.distance)}\n"
            f"- Average Heart Rate: {activity.heart_rate_avg:.0f} bpm\n"
            f"- Maximum Heart Rate: {activity.heart_rate_max:.0f} bpm\n"
            f"- Elevation Gain: {activity.elevation_gain:.0f}m\n"
            + (f"- Average Cadence: {activity.cadence_avg:.0f} spm\n" if activity.cadence_avg else "")
            + (f"- Maximum Cadence: {activity.cadence_max:.0f} spm\n" if activity.cadence_max else "")
            + (f"- Training Effect: {activity.training_effect:.1f}\n" if activity.training_effect else "")
            + (f"- VO2 Max: {activity.vo2_max:.1f}\n" if activity.vo2_max else "")
            + (f"- Suggested Recovery Time: {activity.recovery_time} hours\n" if activity.recovery_time else "")
            + (f"- Temperature: {activity.temperature:.1f}°C\n" if activity.temperature else "")
            + "\nKilometer Splits:\n"
            + "\n".join([
                f"  Km {i+1}: {self._calculate_pace(split['duration'], split['distance'])} "
                f"| HR: {split['heart_rate']:.0f} bpm "
                f"| Cadence: {split['cadence']:.0f} spm"
                for i, split in enumerate(activity.splits)
            ]) if activity.splits else ""
            for idx, activity in enumerate(reversed(activities))
        ])