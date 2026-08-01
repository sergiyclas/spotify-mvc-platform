# src/pl/schemas.py

"""Pydantic models for API request/response validation"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field

# ==================== User Schemas ====================


class SubscriptionBase(BaseModel):
    type: str
    auto_renew: bool = True


class SubscriptionResponse(SubscriptionBase):
    id: int
    start_date: datetime
    end_date: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    email: EmailStr
    username: str


class UserCreate(UserBase):
    subscription_type: str = Field(default="FREE", description="FREE, PREMIUM, or STUDENT")


class UserResponse(UserBase):
    id: int
    subscription_type: str
    registration_date: datetime

    class Config:
        from_attributes = True


class UserDetailResponse(UserResponse):
    playlists: List["PlaylistSummary"] = []


# ==================== Song Schemas ====================


class SongBase(BaseModel):
    title: str
    artist: str
    duration: int = Field(..., description="Duration in milliseconds")
    genre: Optional[str] = None


class SongCreate(SongBase):
    pass


class SongResponse(SongBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== Playlist Schemas ====================


class PlaylistBase(BaseModel):
    name: str
    description: Optional[str] = None


class PlaylistCreate(PlaylistBase):
    owner_id: int


class PlaylistSummary(BaseModel):
    id: int
    name: str
    song_count: int
    created_at: datetime

    class Config:
        from_attributes = True


class PlaylistDetailResponse(PlaylistBase):
    id: int
    owner_id: int
    song_count: int
    songs: List[SongResponse] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== Import Schemas ====================


class ImportResponse(BaseModel):
    status: str
    message: str
    statistics: dict


# ==================== Statistics Schemas ====================


class StatisticsResponse(BaseModel):
    total_users: int
    total_songs: int
    total_playlists: int
    total_playlist_songs: int
    subscriptions: dict
    average_playlist_size: float


# ==================== Error Schemas ====================


class ErrorResponse(BaseModel):
    status: str = "error"
    detail: str
    code: Optional[str] = None


# Update forward references
UserDetailResponse.model_rebuild()
