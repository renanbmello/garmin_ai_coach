import uvicorn
from infrastructure.database_init import init_database
from infrastructure.logging_config import setup_logging

if __name__ == "__main__":
    setup_logging()
    
    uvicorn.run(
        "interfaces.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
