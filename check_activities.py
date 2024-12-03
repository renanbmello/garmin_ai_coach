from sqlalchemy import create_engine, text
import os

# Use a mesma URL do seu arquivo database.py
DATABASE_URL = "postgresql://garmin_user:senhagarminia@localhost/garmin_ai_coach"

def check_activities():
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        # Conta total de atividades
        result = conn.execute(text("SELECT COUNT(*) FROM activities"))
        total = result.scalar()
        print(f"\nTotal de atividades: {total}")
        
        # Lista as 5 atividades mais recentes
        result = conn.execute(text("""
            SELECT activity_type, start_time, distance, duration 
            FROM activities 
            ORDER BY start_time DESC 
            LIMIT 5
        """))
        
        print("\nÚltimas 5 atividades:")
        for row in result:
            print(f"Tipo: {row.activity_type}, Data: {row.start_time}, "
                  f"Distância: {row.distance:.2f}km, Duração: {row.duration:.0f}min")

if __name__ == "__main__":
    check_activities() 