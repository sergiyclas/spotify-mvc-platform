# main.py
"""
Main entry point for the Spotify application
Run with: python main.py
"""
import os
import sys

# Add src directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import uvicorn

from src.common.logger import get_logger
from src.dal import init_db
from src.main import app

logger = get_logger(__name__)

def main():
    """Run the FastAPI application"""
    logger.info("Starting Spotify Platform API...")
    
    # Initialize database
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        return 1
    
    # Run the application
    uvicorn.run(
        app,
        host="localhost",
        port=8000,
        log_level="info"
    )
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
