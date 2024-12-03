from typing import List, Any
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
        
        print("\n=== PROMPT PARA O GPT-4 ===\n")
        print("System message:")
        print("""You are an experienced running coach specializing in training data analysis and periodization. 
        Focus on practical insights and detailed analysis of running metrics including pace, heart rate, cadence, 
        and training effect. Consider the relationship between these metrics and their impact on performance and recovery. This data is from Garmin device.""")
        
        print("\nUser message:")
        print(f"""
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
        """)
        print("\n=== FIM DO PROMPT ===\n")
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system", 
                        "content": """You are an experienced running coach specializing in training data analysis and periodization. 
                        Focus on practical insights and detailed analysis of running metrics including pace, heart rate, cadence, 
                        and training effect. Consider the relationship between these metrics and their impact on performance and recovery. This data is from Garmin device."""
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
            
            if getattr(activity, 'activity_name', None):
                activity_lines.append(f"- Activity Name: {activity.activity_name}")
                
            activity_lines.extend([
                f"- Duration: {format_duration(activity.duration)} (Moving: {format_duration(getattr(activity, 'moving_duration', None))})",
                f"- Distance: {(activity.distance / 1000):.2f} km",
                f"- Average Pace: {format_pace(getattr(activity, 'average_speed', None))}",
                f"- Best Pace: {format_pace(getattr(activity, 'max_speed', None))}",
                f"- Heart Rate: {safe_format(activity.heart_rate_avg, '{:.0f}')} bpm (max: {safe_format(activity.heart_rate_max, '{:.0f}')} bpm)",
                f"- Cadence: {safe_format(getattr(activity, 'cadence_avg', None), '{:.0f}')} spm (max: {safe_format(getattr(activity, 'cadence_max', None), '{:.0f}')} spm)",
                f"- Elevation: gain {safe_format(activity.elevation_gain, '{:.0f}')}m, loss {safe_format(getattr(activity, 'elevation_loss', None), '{:.0f}')}m (min: {safe_format(getattr(activity, 'min_elevation', None), '{:.0f}')}m, max: {safe_format(getattr(activity, 'max_elevation', None), '{:.0f}')}m)"
            ])

            if getattr(activity, 'training_effect', None) is not None:
                activity_lines.append(
                    f"- Training Effect: {safe_format(getattr(activity, 'training_effect', None))} "
                    f"({getattr(activity, 'training_effect_label', 'N/A')}) - "
                    f"{getattr(activity, 'training_effect_message', 'N/A')}"
                )

            if getattr(activity, 'anaerobic_effect', None) is not None:
                activity_lines.append(f"- Anaerobic Effect: {safe_format(getattr(activity, 'anaerobic_effect', None))}")

            if getattr(activity, 'vo2_max', None) is not None:
                activity_lines.append(f"- VO2 Max: {safe_format(getattr(activity, 'vo2_max', None))}")

            if getattr(activity, 'power_avg', None) is not None:
                activity_lines.append(
                    f"- Power: {safe_format(getattr(activity, 'power_avg', None), '{:.0f}')}W "
                    f"(max: {safe_format(getattr(activity, 'power_max', None), '{:.0f}')}W)"
                )

            if any(getattr(activity, attr, None) is not None 
                  for attr in ['stride_length', 'ground_contact_time', 'vertical_oscillation', 'vertical_ratio']):
                activity_lines.extend([
                    "- Running Dynamics:",
                    f"  * Stride Length: {safe_format(getattr(activity, 'stride_length', None), '{:.1f}')}cm",
                    f"  * Ground Contact Time: {safe_format(getattr(activity, 'ground_contact_time', None), '{:.0f}')}ms",
                    f"  * Vertical Oscillation: {safe_format(getattr(activity, 'vertical_oscillation', None), '{:.1f}')}cm",
                    f"  * Vertical Ratio: {safe_format(getattr(activity, 'vertical_ratio', None), '{:.1f}')}%"
                ])

            if getattr(activity, 'intensity_minutes', None):
                activity_lines.append(
                    f"- Intensity Minutes: {getattr(activity, 'intensity_minutes', {}).get('moderate', 0)} moderate, "
                    f"{getattr(activity, 'intensity_minutes', {}).get('vigorous', 0)} vigorous"
                )

            if getattr(activity, 'steps', None):
                activity_lines.append(f"- Steps: {activity.steps}")

            if getattr(activity, 'temperature', None) is not None:
                activity_lines.append(
                    f"- Weather: {safe_format(activity.temperature, '{:.1f}')}°C "
                    f"(Feels like: {safe_format(activity.feels_like, '{:.1f}')}°C, "
                    f"Humidity: {safe_format(activity.humidity, '{:.0f')}%)"
                )

            if getattr(activity, 'avg_stress', None) is not None:
                activity_lines.append(
                    f"- Stress Level: {activity.avg_stress} avg "
                    f"(max: {activity.max_stress})"
                )

            if getattr(activity, 'training_load', None) is not None:
                activity_lines.append(f"- Training Load: {activity.training_load}")

            if getattr(activity, 'training_status', None):
                activity_lines.append(f"- Training Status: {activity.training_status}")

            if getattr(activity, 'performance_condition', None) is not None:
                activity_lines.append(f"- Performance Condition: {activity.performance_condition}")

            # Splits
            if getattr(activity, 'splits', None):
                activity_lines.append("\nKilometer Splits:")
                for i, split in enumerate(activity.splits):
                    activity_lines.append(
                        f"  Km {i+1}: {format_pace(split.get('pace'))} "
                        f"| Elevation: +{safe_format(split.get('elevation_gain'), '{:.0f}')}m"
                    )

            activities_text.append("\n".join(activity_lines))
            print(activity_lines)

        return "\n\n".join(activities_text)