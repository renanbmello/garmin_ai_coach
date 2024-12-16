import logging
import requests
from typing import List, Any
import openai
import os
from domain.entities.activity import Activity

logger = logging.getLogger(__name__)

class LLMAnalyzer:
    def __init__(self, repository=None):
        self.repository = repository
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.xai_api_url = "https://api.x.ai/v1/chat/completions"
        self.xai_api_key = os.getenv("X_API_KEY")

    async def analyze_activities(self, activities: List[Activity]) -> dict:
        """Analyze activities using LLM"""
        try:
            running_activities = [a for a in activities if a.activity_type.lower() == "running"]
            running_activities = running_activities[:10]
            
            context = self._prepare_activity_context(running_activities)
            
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

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.xai_api_key}"
            }
            payload = {
                "messages": [
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                "model": "grok-beta",
                "stream": False,
                "temperature": 0
            }

            xAIResponse = requests.post(
                self.xai_api_url,
                headers=headers,
                json=payload
            )

            xAIResponse.raise_for_status()
            analysisXAI = xAIResponse.json()

            # Chamada para o GPT-4
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ]
            )

            analysis_result = response.choices[0].message.content

            return {
                "analysis": analysis_result,
                "analysisXAI": analysisXAI
            }
            
        except Exception as e:
            logger.error(f"Error analyzing activities: {str(e)}")
            raise

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
        
        def format_pace(speed_ms: float) -> str:
            """Converte velocidade em m/s para pace em min/km"""
            if not speed_ms or speed_ms <= 0:
                return "N/A"
            try:
                minutes_per_km = (1000 / speed_ms) / 60
                minutes = int(minutes_per_km)
                seconds = int((minutes_per_km - minutes) * 60)
                return f"{minutes}:{seconds:02d}/km"
            except:
                return "N/A"

        def format_duration(seconds: float) -> str:
            """convert duration in seconds to HH:MM:SS format"""
            if not seconds:
                return "N/A"
            
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            secs = int(seconds % 60)
            
            if hours > 0:
                return f"{hours}:{minutes:02d}:{secs:02d}"
            return f"{minutes:02d}:{secs:02d}"

        def safe_format(value: Any, format_str: str = '{}') -> str:
            """Format value with None handling"""
            if value is None or (isinstance(value, (int, float)) and value <= 0):
                return "N/A"
            try:
                return format_str.format(value)
            except:
                return "N/A"

        activities_text = []
        for idx, activity in enumerate(reversed(activities)):
            activity_lines = [
                f"Running {idx+1} ({activity.start_time.strftime('%Y-%m-%d %H:%M')}):"
            ]
            
            activity_name = getattr(activity, 'activity_name', None)
            if activity_name:
                activity_lines.append(f"- Activity Name: {activity_name}")
                
            activity_lines.extend([
                f"- Duration: {format_duration(activity.duration)} (Moving: {format_duration(activity.moving_duration)})",
                f"- Distance: {(activity.distance / 1000):.2f} km",
                f"- Average Pace: {activity.pace_formatted}",
                f"- Best Pace: {format_pace(activity.max_speed)}",
                f"- Heart Rate: {safe_format(activity.heart_rate_avg, '{:.0f}')} bpm (max: {safe_format(activity.heart_rate_max, '{:.0f}')} bpm)",
                f"- Cadence: {safe_format(activity.cadence_avg, '{:.0f}')} spm (max: {safe_format(activity.cadence_max, '{:.0f}')} spm)",
                f"- Elevation: gain {safe_format(activity.elevation_gain, '{:.0f}')}m, loss {safe_format(activity.elevation_loss, '{:.0f}')}m (min: {safe_format(activity.min_elevation, '{:.0f}')}m, max: {safe_format(activity.max_elevation, '{:.0f}')}m)"
            ])

            if activity.training_effect is not None:
                activity_lines.append(
                    f"- Training Effect: {safe_format(activity.training_effect)} "
                    f"({activity.training_effect_label or 'N/A'}) - "
                    f"{activity.training_effect_message or 'N/A'}"
                )

            if activity.anaerobic_effect is not None:
                activity_lines.append(f"- Anaerobic Effect: {safe_format(activity.anaerobic_effect)}")

            if activity.vo2_max is not None:
                activity_lines.append(f"- VO2 Max: {safe_format(activity.vo2_max)}")

            if activity.power_avg is not None:
                activity_lines.append(
                    f"- Power: {safe_format(activity.power_avg, '{:.0f}')}W "
                    f"(max: {safe_format(activity.power_max, '{:.0f}')}W)"
                )

            running_dynamics_attrs = ['stride_length', 'ground_contact_time', 'vertical_oscillation', 'vertical_ratio']
            if any(getattr(activity, attr, None) is not None for attr in running_dynamics_attrs):
                activity_lines.extend([
                    "- Running Dynamics:",
                    f"  *  Length: {safe_format(activity.stride_length, '{:.1f}')}cm",
                    f"  * Ground Contact Time: {safe_format(activity.ground_contact_time, '{:.0f}')}ms",
                    f"  * Vertical Oscillation: {safe_format(activity.vertical_oscillation, '{:.1f}')}cm",
                    f"  * Vertical Ratio: {safe_format(activity.vertical_ratio, '{:.1f}')}%"
                ])

            if activity.intensity_minutes:
                moderate = activity.intensity_minutes.get('moderate', 0)
                vigorous = activity.intensity_minutes.get('vigorous', 0)
                activity_lines.append(
                    f"- Intensity Minutes: {moderate} moderate, {vigorous} vigorous"
                )

            if activity.steps:
                activity_lines.append(f"- Steps: {activity.steps}")

            # Splits
            if activity.splits:
                activity_lines.append("\nKilometer Splits:")
                for i, split in enumerate(activity.splits):
                    activity_lines.append(
                        f"  Km {i+1}: {format_pace(split.get('pace'))} "
                        f"| Elevation: +{safe_format(split.get('elevation_gain'), '{:.0f}')}m"
                    )

            activities_text.append("\n".join(activity_lines))

        return "\n\n".join(activities_text)