import sys
import os

# Adiciona o diretório raiz ao PYTHONPATH
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from infrastructure.database_init import init_database

if __name__ == "__main__":
    init_database() 