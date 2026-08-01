# src/dal/models.py

"""SQLAlchemy entity models for Spotify application"""

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship

from src.dal.database import Base

# Association table for Many-to-Many relationship between Playlist and Song
playlist_song_association = Table(
    "playlist_song",
    Base.metadata,
    Column("playlist_id", Integer, ForeignKey("playlist.id", ondelete="CASCADE"), primary_key=True),
    Column("song_id", Integer, ForeignKey("song.id", ondelete="CASCADE"), primary_key=True),
)


class Song(Base):
    """Song/Track entity"""

    __tablename__ = "song"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    artist = Column(String, nullable=False, index=True)
    duration = Column(Integer, nullable=False)  # in milliseconds
    genre = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    playlists = relationship(
        "Playlist", secondary=playlist_song_association, back_populates="songs"
    )

    def __repr__(self):
        return f"<Song id={self.id} title='{self.title}' artist='{self.artist}'>"


class Playlist(Base):
    """Playlist entity"""

    __tablename__ = "playlist"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(String, nullable=True)
    owner_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    owner = relationship("User", back_populates="playlists")
    songs = relationship("Song", secondary=playlist_song_association, back_populates="playlists")

    def __repr__(self):
        return f"<Playlist id={self.id} name='{self.name}' owner_id={self.owner_id}>"


class Subscription(Base):
    """Base Subscription entity (Abstract)"""

    __tablename__ = "subscription"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, nullable=False, index=True)  # Discriminator column
    auto_renew = Column(Boolean, default=True)
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="subscription", uselist=False)

    # Polymorphic identity
    __mapper_args__ = {"polymorphic_identity": "subscription", "polymorphic_on": type}

    def __repr__(self):
        return f"<{self.__class__.__name__} id={self.id}>"


class FreeSubscription(Subscription):
    """Free subscription (no payment)"""

    __mapper_args__ = {
        "polymorphic_identity": "FreeSubscription",
    }


class PremiumSubscription(Subscription):
    """Premium subscription ($9.99/month)"""

    __mapper_args__ = {
        "polymorphic_identity": "PremiumSubscription",
    }


class StudentSubscription(Subscription):
    """Student subscription ($4.99/month)"""

    __mapper_args__ = {
        "polymorphic_identity": "StudentSubscription",
    }


class User(Base):
    """User entity"""

    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    username = Column(String, nullable=False)
    registration_date = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    subscription_id = Column(Integer, ForeignKey("subscription.id"), nullable=False)

    # Relationships
    subscription = relationship("Subscription", back_populates="user", uselist=False)
    playlists = relationship("Playlist", back_populates="owner", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User id={self.id} email='{self.email}' username='{self.username}'>"
