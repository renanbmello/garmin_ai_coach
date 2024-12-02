from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from infrastructure.database import Base, DATABASE_URL
from domain.models.activity import Activity  # Importa o modelo para criar a tabela

def init_database():
    """Initialize the database and create all tables"""
    engine = create_engine(DATABASE_URL)
    
    # Cria todas as tabelas definidas nos modelos
    Base.metadata.create_all(bind=engine)
    
    print("Database initialized successfully!")

if __name__ == "__main__":
    init_database() 