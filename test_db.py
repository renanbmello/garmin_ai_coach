from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

DATABASE_URL = "postgresql://garmin_user:senhagarminia@localhost/garmin_ai_coach"

def test_connection():
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as connection:
            print("Conexão bem sucedida!")
    except SQLAlchemyError as e:
        print(f"Erro ao conectar: {str(e)}")

if __name__ == "__main__":
    test_connection() 