# src/dal/repositories.py

"""Data Access Layer - Repository implementation"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import and_
from sqlalchemy.orm import Session

from src.common.logger import get_logger
from src.dal.models import (
    FreeSubscription,
    Playlist,
    PremiumSubscription,
    Song,
    StudentSubscription,
    Subscription,
    User,
)

logger = get_logger(__name__)


class IDataAccessLayer:
    """Interface for Data Access Layer"""

    # User operations
    async def get_user_by_email(self, email: str) -> Optional[User]:
        raise NotImplementedError

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        raise NotImplementedError

    async def create_user(self, email: str, username: str, subscription_type: str) -> User:
        raise NotImplementedError

    async def get_all_users(self) -> List[User]:
        raise NotImplementedError

    # Song operations
    async def get_song_by_title_and_artist(self, title: str, artist: str) -> Optional[Song]:
        raise NotImplementedError

    async def get_song_by_id(self, song_id: int) -> Optional[Song]:
        raise NotImplementedError

    async def create_song(self, title: str, artist: str, duration: int, genre: str = None) -> Song:
        raise NotImplementedError

    async def get_all_songs(self) -> List[Song]:
        raise NotImplementedError

    async def update_song(self, song_id: int, **kwargs) -> Optional[Song]:
        raise NotImplementedError

    async def delete_song(self, song_id: int) -> bool:
        raise NotImplementedError

    # Playlist operations
    async def get_playlist_by_name_and_owner(self, name: str, owner_id: int) -> Optional[Playlist]:
        raise NotImplementedError

    async def get_playlist_by_id(self, playlist_id: int) -> Optional[Playlist]:
        raise NotImplementedError

    async def create_playlist(self, name: str, owner_id: int, description: str = None) -> Playlist:
        raise NotImplementedError

    async def add_song_to_playlist(self, playlist_id: int, song_id: int) -> None:
        raise NotImplementedError

    async def remove_song_from_playlist(self, playlist_id: int, song_id: int) -> bool:
        raise NotImplementedError

    async def get_all_playlists(self) -> List[Playlist]:
        raise NotImplementedError

    async def update_playlist(self, playlist_id: int, **kwargs) -> Optional[Playlist]:
        raise NotImplementedError

    async def delete_playlist(self, playlist_id: int) -> bool:
        raise NotImplementedError


class DataAccessService(IDataAccessLayer):
    """Repository implementation with SQLAlchemy"""

    def __init__(self, db: Session):
        self.db = db
        logger.info("DataAccessService initialized")

    # ==================== User Operations ====================

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Find user by email with relationships loaded"""
        user = self.db.query(User).filter(User.email == email).first()
        if user:
            # Load relationships
            _ = user.subscription
            _ = user.playlists
        return user

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Find user by ID"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if user:
            _ = user.subscription
            _ = user.playlists
        return user

    async def create_user(self, email: str, username: str, subscription_type: str) -> User:
        """Create new user with specified subscription type"""
        # Check if user already exists
        existing_user = await self.get_user_by_email(email)
        if existing_user:
            logger.warning(f"User with email {email} already exists")
            return existing_user

        # Create subscription based on type
        subscription = self._create_subscription(subscription_type)

        # Create user
        user = User(email=email, username=username, subscription=subscription)

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        logger.info(f"User created: {email} with {subscription_type} subscription")
        return user

    async def get_all_users(self) -> List[User]:
        """Get all users"""
        users = self.db.query(User).all()
        logger.info(f"Retrieved {len(users)} users")
        return users

    # ==================== Song Operations ====================

    async def get_song_by_title_and_artist(self, title: str, artist: str) -> Optional[Song]:
        """Find song by title and artist"""
        song = self.db.query(Song).filter(and_(Song.title == title, Song.artist == artist)).first()
        return song

    async def get_song_by_id(self, song_id: int) -> Optional[Song]:
        """Find song by ID"""
        return self.db.query(Song).filter(Song.id == song_id).first()

    async def create_song(self, title: str, artist: str, duration: int, genre: str = None) -> Song:
        """Create new song or return existing"""
        # Check if song already exists
        existing_song = await self.get_song_by_title_and_artist(title, artist)
        if existing_song:
            logger.debug(f"Song already exists: {title} by {artist}")
            return existing_song

        song = Song(title=title, artist=artist, duration=duration, genre=genre)

        self.db.add(song)
        self.db.commit()
        self.db.refresh(song)

        logger.debug(f"Song created: {title} by {artist}")
        return song

    async def get_all_songs(self) -> List[Song]:
        """Get all songs"""
        songs = self.db.query(Song).all()
        logger.info(f"Retrieved {len(songs)} songs")
        return songs

    async def update_song(
        self, song_id: int, title: str = None, artist: str = None, 
        duration: int = None, genre: str = None
    ) -> Optional[Song]:
        """Update song details"""
        song = await self.get_song_by_id(song_id)
        if not song:
            logger.warning(f"Song {song_id} not found")
            return None

        if title:
            song.title = title
        if artist:
            song.artist = artist
        if duration is not None:
            song.duration = duration
        if genre:
            song.genre = genre

        self.db.commit()
        self.db.refresh(song)
        logger.info(f"Song updated: {song_id}")
        return song

    async def delete_song(self, song_id: int) -> bool:
        """Delete song by ID"""
        song = await self.get_song_by_id(song_id)
        if not song:
            logger.warning(f"Song {song_id} not found")
            return False

        self.db.delete(song)
        self.db.commit()
        logger.info(f"Song deleted: {song_id}")
        return True

    # ==================== Playlist Operations ====================

    async def get_playlist_by_name_and_owner(self, name: str, owner_id: int) -> Optional[Playlist]:
        """Find playlist by name and owner"""
        playlist = (
            self.db.query(Playlist)
            .filter(and_(Playlist.name == name, Playlist.owner_id == owner_id))
            .first()
        )
        if playlist:
            _ = playlist.songs
        return playlist

    async def get_playlist_by_id(self, playlist_id: int) -> Optional[Playlist]:
        """Find playlist by ID"""
        playlist = self.db.query(Playlist).filter(Playlist.id == playlist_id).first()
        if playlist:
            _ = playlist.songs
        return playlist

    async def create_playlist(self, name: str, owner_id: int, description: str = None) -> Playlist:
        """Create new playlist or return existing"""
        # Check if playlist already exists for this owner
        existing_playlist = await self.get_playlist_by_name_and_owner(name, owner_id)
        if existing_playlist:
            logger.debug(f"Playlist '{name}' already exists for user {owner_id}")
            return existing_playlist

        playlist = Playlist(name=name, owner_id=owner_id, description=description)

        self.db.add(playlist)
        self.db.commit()
        self.db.refresh(playlist)

        logger.debug(f"Playlist created: '{name}' for user {owner_id}")
        return playlist

    async def add_song_to_playlist(self, playlist_id: int, song_id: int) -> None:
        """Add song to playlist"""
        playlist = await self.get_playlist_by_id(playlist_id)
        song = await self.get_song_by_id(song_id)

        if not playlist or not song:
            logger.warning(f"Playlist {playlist_id} or Song {song_id} not found")
            return

        # Check if song already in playlist
        if song not in playlist.songs:
            playlist.songs.append(song)
            playlist.updated_at = datetime.utcnow()
            self.db.commit()
            logger.debug(f"Song {song_id} added to Playlist {playlist_id}")

    async def get_all_playlists(self) -> List[Playlist]:
        """Get all playlists"""
        playlists = self.db.query(Playlist).all()
        logger.info(f"Retrieved {len(playlists)} playlists")
        return playlists

    async def update_playlist(
        self, playlist_id: int, name: str = None, description: str = None
    ) -> Optional[Playlist]:
        """Update playlist details"""
        playlist = await self.get_playlist_by_id(playlist_id)
        if not playlist:
            logger.warning(f"Playlist {playlist_id} not found")
            return None

        if name:
            playlist.name = name
        if description is not None:
            playlist.description = description

        playlist.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(playlist)
        logger.info(f"Playlist updated: {playlist_id}")
        return playlist

    async def delete_playlist(self, playlist_id: int) -> bool:
        """Delete playlist by ID"""
        playlist = await self.get_playlist_by_id(playlist_id)
        if not playlist:
            logger.warning(f"Playlist {playlist_id} not found")
            return False

        self.db.delete(playlist)
        self.db.commit()
        logger.info(f"Playlist deleted: {playlist_id}")
        return True

    async def remove_song_from_playlist(self, playlist_id: int, song_id: int) -> bool:
        """Remove song from playlist"""
        playlist = await self.get_playlist_by_id(playlist_id)
        song = await self.get_song_by_id(song_id)

        if not playlist or not song:
            logger.warning(f"Playlist {playlist_id} or Song {song_id} not found")
            return False

        if song in playlist.songs:
            playlist.songs.remove(song)
            playlist.updated_at = datetime.utcnow()
            self.db.commit()
            logger.info(f"Song {song_id} removed from Playlist {playlist_id}")
            return True

        logger.warning(f"Song {song_id} not in Playlist {playlist_id}")
        return False

    # ==================== Subscription Factory ====================

    def _create_subscription(self, subscription_type: str) -> Subscription:
        """Factory pattern for subscription creation"""
        sub_type = subscription_type.upper()

        if sub_type == "PREMIUM":
            return PremiumSubscription(type="PremiumSubscription")
        elif sub_type == "STUDENT":
            return StudentSubscription(type="StudentSubscription")
        else:  # Default to FREE
            return FreeSubscription(type="FreeSubscription")
