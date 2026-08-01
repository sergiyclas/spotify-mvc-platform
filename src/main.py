# src/main.py

"""Main FastAPI application"""

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from config import API_DESCRIPTION, API_TITLE, API_VERSION
from src.common.logger import get_logger
from src.dal import init_db
from src.pl import api_router, router

logger = get_logger(__name__)

# Initialize database
init_db()

# Create FastAPI app
app = FastAPI(title=API_TITLE, version=API_VERSION, description=API_DESCRIPTION)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup static files
static_path = Path(__file__).parent.parent / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# Include routers
app.include_router(router)
app.include_router(api_router)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    logger.info("Application starting up...")
    init_db()
    logger.info("Database initialized")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Application shutting down...")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
