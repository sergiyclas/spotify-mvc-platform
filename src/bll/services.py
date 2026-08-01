# src/bll/services.py

"""Business Logic Layer - Services"""

import csv
from pathlib import Path
from typing import Any, Dict, List

from src.common.logger import get_logger
from src.dal.models import Playlist, Song, User
from src.dal.repositories import DataAccessService

logger = get_logger(__name__)


class SpotifyService:
    """Main Spotify service for CSV import and data management"""

    def __init__(self, dal: DataAccessService):
        self.dal = dal
        logger.info("SpotifyService initialized")

    async def import_csv(self, csv_file_path: str) -> Dict[str, int]:
        """
        Import data from CSV file

        CSV format: email, subType, playlistName, songTitle, artist, duration, genre

        Returns:
            Dict with counts: {'users': X, 'songs': Y, 'playlists': Z}
        """
        stats = {
            "users_created": 0,
            "users_existing": 0,
            "songs_created": 0,
            "playlists_created": 0,
            "associations_added": 0,
            "total_rows": 0,
        }

        try:
            csv_path = Path(csv_file_path)
            if not csv_path.exists():
                logger.error(f"CSV file not found: {csv_file_path}")
                raise FileNotFoundError(f"CSV file not found: {csv_file_path}")

            logger.info(f"Starting CSV import from {csv_file_path}")

            with open(csv_path, "r", encoding="utf-8") as file:
                reader = csv.DictReader(file)

                for row_num, row in enumerate(reader, start=2):  # Start from 2 (header is row 1)
                    try:
                        stats["total_rows"] += 1

                        # Extract data
                        email = row.get("email", "").strip()
                        sub_type = row.get("subType", "FREE").strip()
                        playlist_name = row.get("playlistName", "").strip()
                        song_title = row.get("songTitle", "").strip()
                        artist = row.get("artist", "").strip()
                        duration_str = row.get("duration", "0").strip()
                        genre = row.get("genre", "").strip()

                        # Validate required fields
                        if not all([email, playlist_name, song_title, artist]):
                            logger.warning(f"Row {row_num}: Missing required fields, skipping")
                            continue

                        # Parse duration
                        try:
                            duration = int(duration_str)
                        except ValueError:
                            logger.warning(
                                f"Row {row_num}: Invalid duration '{duration_str}', using 0"
                            )
                            duration = 0

                        # Create/get Song
                        song = await self.dal.create_song(song_title, artist, duration, genre)
                        if song.id is None:
                            stats["songs_created"] += 1
                        else:
                            stats["songs_created"] += 1  # Count each creation attempt

                        # Create/get User
                        existing_user = await self.dal.get_user_by_email(email)
                        if existing_user:
                            # If user exists, check if subscription type differs
                            user = existing_user
                            stats["users_existing"] += 1
                            logger.debug(f"User {email} already exists, reusing")
                        else:
                            user = await self.dal.create_user(email, email.split("@")[0], sub_type)
                            stats["users_created"] += 1

                        # Create/get Playlist
                        playlist = await self.dal.create_playlist(playlist_name, user.id)
                        stats["playlists_created"] += 1

                        # Add song to playlist
                        await self.dal.add_song_to_playlist(playlist.id, song.id)
                        stats["associations_added"] += 1

                        if row_num % 50 == 0:
                            logger.info(f"Processed {row_num} rows...")

                    except Exception as e:
                        logger.error(f"Error processing row {row_num}: {str(e)}")
                        continue

            logger.info(f"CSV import completed: {stats}")
            return stats

        except Exception as e:
            logger.error(f"CSV import failed: {str(e)}")
            raise

    async def get_all_users(self) -> List[User]:
        """Get all users"""
        return await self.dal.get_all_users()

    async def get_all_songs(self) -> List[Song]:
        """Get all songs"""
        return await self.dal.get_all_songs()

    async def get_all_playlists(self) -> List[Playlist]:
        """Get all playlists"""
        return await self.dal.get_all_playlists()

    async def get_user_with_playlists(self, user_id: int) -> Dict[str, Any]:
        """Get user with their playlists and songs"""
        user = await self.dal.get_user_by_id(user_id)

        if not user:
            return None

        return {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "subscription_type": user.subscription.type,
            "registration_date": user.registration_date.isoformat(),
            "playlists": [
                {
                    "id": playlist.id,
                    "name": playlist.name,
                    "song_count": len(playlist.songs),
                    "created_at": playlist.created_at.isoformat(),
                }
                for playlist in user.playlists
            ],
        }

    async def get_playlist_with_songs(self, playlist_id: int) -> Dict[str, Any]:
        """Get playlist with all songs"""
        playlist = await self.dal.get_playlist_by_id(playlist_id)

        if not playlist:
            return None

        return {
            "id": playlist.id,
            "name": playlist.name,
            "description": playlist.description,
            "owner_id": playlist.owner_id,
            "song_count": len(playlist.songs),
            "songs": [
                {
                    "id": song.id,
                    "title": song.title,
                    "artist": song.artist,
                    "duration": song.duration,
                    "genre": song.genre,
                }
                for song in playlist.songs
            ],
            "created_at": playlist.created_at.isoformat(),
            "updated_at": playlist.updated_at.isoformat(),
        }

    # ==================== CRUD Operations ====================

    async def create_song_direct(self, title: str, artist: str, duration: int, genre: str = None) -> Song:
        """Create a new song"""
        return await self.dal.create_song(title, artist, duration, genre)

    async def update_song_direct(self, song_id: int, title: str = None, artist: str = None,
                                  duration: int = None, genre: str = None) -> Dict[str, Any]:
        """Update song"""
        song = await self.dal.update_song(song_id, title=title, artist=artist, 
                                         duration=duration, genre=genre)
        if not song:
            return {"status": "error", "message": "Song not found"}
        
        return {
            "status": "success",
            "id": song.id,
            "title": song.title,
            "artist": song.artist,
            "duration": song.duration,
            "genre": song.genre,
        }

    async def delete_song_direct(self, song_id: int) -> Dict[str, Any]:
        """Delete song"""
        success = await self.dal.delete_song(song_id)
        if not success:
            return {"status": "error", "message": "Song not found"}
        return {"status": "success", "message": "Song deleted"}

    async def create_playlist_direct(self, name: str, owner_id: int, description: str = None) -> Playlist:
        """Create a new playlist"""
        return await self.dal.create_playlist(name, owner_id, description)

    async def update_playlist_direct(self, playlist_id: int, name: str = None, 
                                     description: str = None) -> Dict[str, Any]:
        """Update playlist"""
        playlist = await self.dal.update_playlist(playlist_id, name=name, description=description)
        if not playlist:
            return {"status": "error", "message": "Playlist not found"}
        
        return {
            "status": "success",
            "id": playlist.id,
            "name": playlist.name,
            "description": playlist.description,
        }

    async def delete_playlist_direct(self, playlist_id: int) -> Dict[str, Any]:
        """Delete playlist"""
        success = await self.dal.delete_playlist(playlist_id)
        if not success:
            return {"status": "error", "message": "Playlist not found"}
        return {"status": "success", "message": "Playlist deleted"}

    async def remove_song_from_playlist_direct(self, playlist_id: int, song_id: int) -> Dict[str, Any]:
        """Remove song from playlist"""
        success = await self.dal.remove_song_from_playlist(playlist_id, song_id)
        if not success:
            return {"status": "error", "message": "Playlist or song not found"}
        return {"status": "success", "message": "Song removed from playlist"}


class StatisticsService:
    """Service for statistics operations"""

    def __init__(self, dal: DataAccessService):
        self.dal = dal
        logger.info("StatisticsService initialized")

    async def get_statistics(self) -> Dict[str, Any]:
        """Get platform statistics"""
        try:
            users = await self.dal.get_all_users()
            songs = await self.dal.get_all_songs()
            playlists = await self.dal.get_all_playlists()

            # Count subscriptions
            subscription_counts = {}
            for user in users:
                sub_type = user.subscription.type
                subscription_counts[sub_type] = subscription_counts.get(sub_type, 0) + 1

            # Calculate total playlist songs
            total_playlist_songs = sum(len(p.songs) for p in playlists)

            stats = {
                "total_users": len(users),
                "total_songs": len(songs),
                "total_playlists": len(playlists),
                "total_playlist_songs": total_playlist_songs,
                "subscriptions": subscription_counts,
                "average_playlist_size": total_playlist_songs / len(playlists) if playlists else 0,
            }

            logger.info(f"Statistics generated: {stats}")
            return stats

        except Exception as e:
            logger.error(f"Error generating statistics: {str(e)}")
            raise
