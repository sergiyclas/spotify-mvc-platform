# cli.py
"""Utility scripts for the Spotify application"""
import asyncio
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.bll import SpotifyService
from src.common.logger import get_logger
from src.dal import DataAccessService, SessionLocal, init_db

logger = get_logger(__name__)

def init_database():
    """Initialize the database"""
    logger.info("Initializing database...")
    init_db()
    logger.info("Database initialized successfully")

async def import_csv_from_file(csv_path: str):
    """Import CSV data"""
    logger.info(f"Starting CSV import from {csv_path}...")
    
    db = SessionLocal()
    try:
        dal = DataAccessService(db)
        service = SpotifyService(dal)
        stats = await service.import_csv(csv_path)
        
        logger.info("Import completed successfully!")
        logger.info(f"Statistics: {stats}")
        return stats
    finally:
        db.close()

def show_statistics():
    """Show database statistics"""
    db = SessionLocal()
    try:
        # Import after database is initialized
        from src.dal import Playlist, Song, User
        
        users = db.query(User).all()
        songs = db.query(Song).all()
        playlists = db.query(Playlist).all()
        
        print(f"\n{'='*50}")
        print("Database Statistics")
        print(f"{'='*50}")
        print(f"Total Users: {len(users)}")
        print(f"Total Songs: {len(songs)}")
        print(f"Total Playlists: {len(playlists)}")
        
        # Subscription breakdown
        subscriptions = {}
        for user in users:
            sub_type = user.subscription.type
            subscriptions[sub_type] = subscriptions.get(sub_type, 0) + 1
        
        print("\nSubscription Breakdown:")
        for sub_type, count in subscriptions.items():
            print(f"  {sub_type}: {count}")
        
        print(f"{'='*50}\n")
        
    finally:
        db.close()

def clean_database():
    """Delete and recreate database"""
    logger.warning("Cleaning database...")
    
    db_path = "spotify.db"
    if os.path.exists(db_path):
        os.remove(db_path)
        logger.info(f"Deleted {db_path}")
    
    init_database()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Spotify Application Utilities")
    parser.add_argument(
        "command",
        choices=["init-db", "import-csv", "stats", "clean"],
        help="Command to execute"
    )
    parser.add_argument(
        "--csv",
        default="spotify_data.csv",
        help="CSV file path for import command"
    )
    
    args = parser.parse_args()
    
    if args.command == "init-db":
        init_database()
    elif args.command == "import-csv":
        asyncio.run(import_csv_from_file(args.csv))
    elif args.command == "stats":
        show_statistics()
    elif args.command == "clean":
        clean_database()
