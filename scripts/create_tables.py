import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from infrastructure.database import Base, DATABASE_URL
from domain.models.activity import Activity  # Importa o modelo para registrá-lo

def create_tables():
    try:
        engine = create_engine(DATABASE_URL)
        Base.metadata.create_all(bind=engine)
        print("Tabelas criadas com sucesso!")
    except SQLAlchemyError as e:
        print(f"Erro ao criar tabelas: {str(e)}")

if __name__ == "__main__":
    create_tables() 