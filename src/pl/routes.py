# src/pl/routes.py

"""Presentation Layer - FastAPI routes"""

from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from src.bll import SpotifyService, StatisticsService
from src.common.logger import get_logger
from src.dal import DataAccessService, get_db
from src.pl.schemas import (
    ImportResponse,
)

router = APIRouter()
api_router = APIRouter(prefix="/api", tags=["spotify"])
logger = get_logger(__name__)

# Setup templates
templates_dir = Path(__file__).parent.parent.parent / "templates"
logger.info(f"Templates directory: {templates_dir}")
logger.info(f"Templates directory exists: {templates_dir.exists()}")
if not templates_dir.exists():
    logger.error(f"Templates directory not found at {templates_dir}")
    raise RuntimeError(f"Templates directory not found at {templates_dir}")
templates = Jinja2Templates(directory=str(templates_dir))
logger.info("Jinja2Templates initialized successfully")


# Dependency: Get SpotifyService
def get_spotify_service(db: Session = Depends(get_db)) -> SpotifyService:
    """Dependency injection for SpotifyService"""
    dal = DataAccessService(db)
    return SpotifyService(dal)


# Dependency: Get StatisticsService
def get_statistics_service(db: Session = Depends(get_db)) -> StatisticsService:
    """Dependency injection for StatisticsService"""
    dal = DataAccessService(db)
    return StatisticsService(dal)


# ==================== HTML Routes ====================


@router.get("/")
async def index(
    request: Request,
    service: StatisticsService = Depends(get_statistics_service),
):
    """Home page"""
    try:
        stats = await service.get_statistics()
        logger.info(f"Stats retrieved: {type(stats)}, {stats}")
        context = {
            "total_users": int(stats.get("total_users", 0)),
            "total_songs": int(stats.get("total_songs", 0)),
            "total_playlists": int(stats.get("total_playlists", 0)),
            "total_subscriptions": int(len(stats.get("subscriptions", {}))),
        }
        logger.info(f"Context created: {context}")
        # Fixed TemplateResponse signature
        response = templates.TemplateResponse(
            request=request, 
            name="index.html", 
            context=context
        )
        logger.info("TemplateResponse created successfully")
        return response
    except Exception as e:
        import traceback
        logger.error(f"Error loading index: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/songs")
async def songs_list(
    request: Request,
    service: SpotifyService = Depends(get_spotify_service),
):
    """Songs list page"""
    try:
        songs = await service.get_all_songs()
        # Fixed TemplateResponse signature
        return templates.TemplateResponse(
            request=request,
            name="songs.html",
            context={"songs": songs}
        )
    except Exception as e:
        logger.error(f"Error loading songs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/songs/create")
async def create_song_form(request: Request):
    """Create song form"""
    try:
        # Fixed TemplateResponse signature
        return templates.TemplateResponse(
            request=request,
            name="song_form.html",
            context={"song": None}
        )
    except Exception as e:
        logger.error(f"Error loading create song form: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/songs/create")
async def create_song(
    request: Request,
    title: str = Form(...),
    artist: str = Form(...),
    duration: int = Form(...),
    genre: str = Form(None),
    service: SpotifyService = Depends(get_spotify_service),
):
    """Create song"""
    try:
        await service.create_song_direct(title, artist, duration, genre)
        return RedirectResponse(url="/songs", status_code=302)
    except Exception as e:
        logger.error(f"Error creating song: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/songs/{song_id}/edit")
async def edit_song_form(
    request: Request,
    song_id: int,
    service: SpotifyService = Depends(get_spotify_service),
):
    """Edit song form"""
    try:
        songs = await service.get_all_songs()
        song = next((s for s in songs if s.id == song_id), None)
        
        if not song:
            raise HTTPException(status_code=404, detail="Song not found")
        
        # Fixed TemplateResponse signature
        return templates.TemplateResponse(
            request=request,
            name="song_form.html",
            context={"song": song}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error loading edit song form: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/songs/{song_id}/edit")
async def update_song(
    request: Request,
    song_id: int,
    title: str = Form(...),
    artist: str = Form(...),
    duration: int = Form(...),
    genre: str = Form(None),
    service: SpotifyService = Depends(get_spotify_service),
):
    """Update song"""
    try:
        result = await service.update_song_direct(song_id, title, artist, duration, genre)
        if result.get("status") != "success":
            raise HTTPException(status_code=404, detail="Song not found")
        return RedirectResponse(url="/songs", status_code=302)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating song: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/songs/{song_id}/delete")
async def delete_song(
    song_id: int,
    service: SpotifyService = Depends(get_spotify_service),
):
    """Delete song"""
    try:
        result = await service.delete_song_direct(song_id)
        if result.get("status") != "success":
            raise HTTPException(status_code=404, detail="Song not found")
        return RedirectResponse(url="/songs", status_code=302)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting song: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/playlists")
async def playlists_list(
    request: Request,
    service: SpotifyService = Depends(get_spotify_service),
):
    """Playlists list page"""
    try:
        playlists = await service.get_all_playlists()
        # Fixed TemplateResponse signature
        return templates.TemplateResponse(
            request=request,
            name="playlists.html",
            context={"playlists": playlists}
        )
    except Exception as e:
        logger.error(f"Error loading playlists: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/playlists/create")
async def create_playlist_form(request: Request):
    """Create playlist form"""
    try:
        # Fixed TemplateResponse signature
        return templates.TemplateResponse(
            request=request,
            name="playlist_form.html",
            context={"playlist": None}
        )
    except Exception as e:
        logger.error(f"Error loading create playlist form: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/playlists/create")
async def create_playlist(
    request: Request,
    name: str = Form(...),
    description: str = Form(None),
    owner_id: int = Form(...),
    service: SpotifyService = Depends(get_spotify_service),
):
    """Create playlist"""
    try:
        await service.create_playlist_direct(name, owner_id, description)
        return RedirectResponse(url="/playlists", status_code=302)
    except Exception as e:
        logger.error(f"Error creating playlist: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/playlists/{playlist_id}")
async def playlist_detail(
    request: Request,
    playlist_id: int,
    service: SpotifyService = Depends(get_spotify_service),
):
    """Playlist detail page"""
    try:
        playlist_data = await service.get_playlist_with_songs(playlist_id)
        if not playlist_data:
            raise HTTPException(status_code=404, detail="Playlist not found")
        
        all_songs = await service.get_all_songs()
        playlist_song_ids = {s["id"] for s in playlist_data.get("songs", [])}
        available_songs = [s for s in all_songs if s.id not in playlist_song_ids]
        
        # Fixed TemplateResponse signature
        return templates.TemplateResponse(
            request=request,
            name="playlist_detail.html",
            context={
                "playlist": playlist_data,
                "songs": playlist_data.get("songs", []),
                "available_songs": available_songs,
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error loading playlist detail: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/playlists/{playlist_id}/edit")
async def edit_playlist_form(
    request: Request,
    playlist_id: int,
    service: SpotifyService = Depends(get_spotify_service),
):
    """Edit playlist form"""
    try:
        playlist_data = await service.get_playlist_with_songs(playlist_id)
        if not playlist_data:
            raise HTTPException(status_code=404, detail="Playlist not found")
        
        # Fixed TemplateResponse signature
        return templates.TemplateResponse(
            request=request,
            name="playlist_form.html",
            context={"playlist": playlist_data}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error loading edit playlist form: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/playlists/{playlist_id}/edit")
async def update_playlist(
    request: Request,
    playlist_id: int,
    name: str = Form(...),
    description: str = Form(None),
    service: SpotifyService = Depends(get_spotify_service),
):
    """Update playlist"""
    try:
        result = await service.update_playlist_direct(playlist_id, name, description)
        if result.get("status") != "success":
            raise HTTPException(status_code=404, detail="Playlist not found")
        return RedirectResponse(url=f"/playlists/{playlist_id}", status_code=302)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating playlist: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/playlists/{playlist_id}/delete")
async def delete_playlist(
    playlist_id: int,
    service: SpotifyService = Depends(get_spotify_service),
):
    """Delete playlist"""
    try:
        result = await service.delete_playlist_direct(playlist_id)
        if result.get("status") != "success":
            raise HTTPException(status_code=404, detail="Playlist not found")
        return RedirectResponse(url="/playlists", status_code=302)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting playlist: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/playlists/{playlist_id}/add-song")
async def add_song_to_playlist(
    playlist_id: int,
    song_id: int = Form(...),
    db: Session = Depends(get_db),
):
    """Add song to playlist"""
    try:
        dal = DataAccessService(db)
        await dal.add_song_to_playlist(playlist_id, song_id)
        return RedirectResponse(url=f"/playlists/{playlist_id}", status_code=302)
    except Exception as e:
        logger.error(f"Error adding song to playlist: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/playlists/{playlist_id}/songs/{song_id}/remove")
async def remove_song_from_playlist(
    playlist_id: int,
    song_id: int,
    db: Session = Depends(get_db),
):
    """Remove song from playlist"""
    try:
        dal = DataAccessService(db)
        success = await dal.remove_song_from_playlist(playlist_id, song_id)
        if not success:
            raise HTTPException(status_code=404, detail="Playlist or song not found")
        return RedirectResponse(url=f"/playlists/{playlist_id}", status_code=302)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing song from playlist: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/statistics")
async def statistics_page(
    request: Request,
    service: StatisticsService = Depends(get_statistics_service),
):
    """Statistics page"""
    try:
        stats = await service.get_statistics()
        # Fixed TemplateResponse signature
        return templates.TemplateResponse(
            request=request,
            name="statistics.html",
            context={"stats": stats}
        )
    except Exception as e:
        logger.error(f"Error loading statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== API Routes ====================


@api_router.post("/import/csv", response_model=ImportResponse)
async def import_csv(
    file: UploadFile = File(...), service: SpotifyService = Depends(get_spotify_service)
):
    """
    Import data from CSV file

    CSV format: email, subType, playlistName, songTitle, artist, duration, genre
    """
    try:
        import os
        import tempfile

        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        try:
            # Import from temporary file
            stats = await service.import_csv(tmp_path)

            logger.info(f"CSV import successful: {stats}")
            return ImportResponse(
                status="success",
                message=f"Successfully imported {stats.get('total_rows', 0)} rows",
                statistics=stats,
            )
        finally:
            # Clean up temporary file
            os.remove(tmp_path)

    except Exception as e:
        logger.error(f"Error importing CSV: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


# ==================== User Routes ====================


@api_router.get("/users")
async def get_all_users(service: SpotifyService = Depends(get_spotify_service)):
    """Get all users on the platform"""
    try:
        users = await service.get_all_users()
        user_responses = [
            {
                "id": u.id,
                "email": u.email,
                "username": u.username,
                "subscription_type": u.subscription.type,
                "registration_date": u.registration_date.isoformat(),
            }
            for u in users
        ]
        return {"status": "success", "count": len(user_responses), "data": user_responses}
    except Exception as e:
        logger.error(f"Error retrieving users: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/users/{user_id}")
async def get_user_detail(user_id: int, service: SpotifyService = Depends(get_spotify_service)):
    """Get user details including their playlists"""
    try:
        user_data = await service.get_user_with_playlists(user_id)
        if not user_data:
            raise HTTPException(status_code=404, detail="User not found")
        return {"status": "success", "data": user_data}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Song Routes ====================


@api_router.get("/songs")
async def get_all_songs(service: SpotifyService = Depends(get_spotify_service)):
    """Get all songs in the platform"""
    try:
        songs = await service.get_all_songs()
        song_responses = [
            {
                "id": s.id,
                "title": s.title,
                "artist": s.artist,
                "duration": s.duration,
                "genre": s.genre,
                "created_at": s.created_at.isoformat(),
            }
            for s in songs
        ]
        return {"status": "success", "count": len(song_responses), "data": song_responses}
    except Exception as e:
        logger.error(f"Error retrieving songs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Playlist Routes ====================


@api_router.get("/playlists")
async def get_all_playlists(service: SpotifyService = Depends(get_spotify_service)):
    """Get all playlists on the platform"""
    try:
        playlists = await service.get_all_playlists()
        playlist_responses = [
            {
                "id": p.id,
                "name": p.name,
                "owner_id": p.owner_id,
                "song_count": len(p.songs),
                "created_at": p.created_at.isoformat(),
            }
            for p in playlists
        ]
        return {"status": "success", "count": len(playlist_responses), "data": playlist_responses}
    except Exception as e:
        logger.error(f"Error retrieving playlists: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/playlists/{playlist_id}")
async def get_playlist_detail(
    playlist_id: int, service: SpotifyService = Depends(get_spotify_service)
):
    """Get playlist details including all songs"""
    try:
        playlist_data = await service.get_playlist_with_songs(playlist_id)
        if not playlist_data:
            raise HTTPException(status_code=404, detail="Playlist not found")
        return {"status": "success", "data": playlist_data}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving playlist {playlist_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Statistics Routes ====================


@api_router.get("/statistics")
async def get_statistics(service: StatisticsService = Depends(get_statistics_service)):
    """Get platform statistics (users, songs, playlists, subscriptions)"""
    try:
        stats = await service.get_statistics()
        return {"status": "success", "data": stats}
    except Exception as e:
        logger.error(f"Error retrieving statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== Health Check ====================


@api_router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "API is running"}