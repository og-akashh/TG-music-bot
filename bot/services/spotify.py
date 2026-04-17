"""
Spotify service for track/playlist extraction and YouTube mapping.
"""

import aiohttp
import asyncio
import base64
from typing import Optional, Dict, Any, List
from bot.config import settings
from bot.services.youtube import YouTubeService
import logging

logger = logging.getLogger(__name__)

class SpotifyService:
    """Service for Spotify API operations."""
    
    _access_token: Optional[str] = None
    _token_expiry: float = 0
    
    @classmethod
    async def _get_access_token(cls) -> Optional[str]:
        """Get or refresh Spotify access token."""
        if cls._access_token and asyncio.get_event_loop().time() < cls._token_expiry:
            return cls._access_token
        
        if not settings.SPOTIFY_CLIENT_ID or not settings.SPOTIFY_CLIENT_SECRET:
            logger.warning("Spotify credentials not configured")
            return None
        
        auth_string = f"{settings.SPOTIFY_CLIENT_ID}:{settings.SPOTIFY_CLIENT_SECRET}"
        auth_bytes = auth_string.encode('utf-8')
        auth_b64 = base64.b64encode(auth_bytes).decode('utf-8')
        
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Basic {auth_b64}",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            data = {"grant_type": "client_credentials"}
            
            try:
                async with session.post(
                    "https://accounts.spotify.com/api/token",
                    headers=headers,
                    data=data
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        cls._access_token = result["access_token"]
                        cls._token_expiry = asyncio.get_event_loop().time() + result["expires_in"] - 60
                        return cls._access_token
                    else:
                        logger.error(f"Spotify auth failed: {response.status}")
                        return None
            except Exception as e:
                logger.error(f"Spotify token error: {e}")
                return None
    
    @classmethod
    async def extract_track(cls, track_id: str) -> Optional[Dict[str, Any]]:
        """
        Extract track information from Spotify.
        
        Args:
            track_id: Spotify track ID
        
        Returns:
            Track information with YouTube mapping
        """
        token = await cls._get_access_token()
        if not token:
            return None
        
        async with aiohttp.ClientSession() as session:
            headers = {"Authorization": f"Bearer {token}"}
            
            try:
                async with session.get(
                    f"https://api.spotify.com/v1/tracks/{track_id}",
                    headers=headers
                ) as response:
                    if response.status != 200:
                        logger.error(f"Spotify API error: {response.status}")
                        return None
                    
                    track = await response.json()
                    
                    # Search YouTube for equivalent track
                    search_query = f"{track['name']} {track['artists'][0]['name']}"
                    youtube_results = await YouTubeService.search(search_query, limit=1)
                    
                    if youtube_results:
                        result = youtube_results[0]
                        result["spotify_id"] = track["id"]
                        result["spotify_url"] = track["external_urls"]["spotify"]
                        result["artists"] = [artist["name"] for artist in track["artists"]]
                        result["album"] = track["album"]["name"]
                        result["source"] = "spotify"
                        return result
                    
                    return None
                    
            except Exception as e:
                logger.error(f"Spotify track extraction failed: {e}")
                return None
    
    @classmethod
    async def extract_playlist(cls, playlist_id: str) -> List[Dict[str, Any]]:
        """
        Extract all tracks from a Spotify playlist.
        
        Args:
            playlist_id: Spotify playlist ID
        
        Returns:
            List of track information with YouTube mapping
        """
        token = await cls._get_access_token()
        if not token:
            return []
        
        async with aiohttp.ClientSession() as session:
            headers = {"Authorization": f"Bearer {token}"}
            tracks = []
            url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
            
            try:
                while url:
                    async with session.get(url, headers=headers) as response:
                        if response.status != 200:
                            logger.error(f"Spotify API error: {response.status}")
                            break
                        
                        data = await response.json()
                        
                        for item in data["items"]:
                            if item["track"] and not item["track"].get("is_local"):
                                track = item["track"]
                                search_query = f"{track['name']} {track['artists'][0]['name']}"
                                youtube_results = await YouTubeService.search(search_query, limit=1)
                                
                                if youtube_results:
                                    result = youtube_results[0]
                                    result["spotify_id"] = track["id"]
                                    result["artists"] = [artist["name"] for artist in track["artists"]]
                                    result["album"] = track["album"]["name"]
                                    result["source"] = "spotify"
                                    tracks.append(result)
                                
                                # Rate limiting
                                await asyncio.sleep(0.1)
                        
                        url = data.get("next")
                
                return tracks
                
            except Exception as e:
                logger.error(f"Spotify playlist extraction failed: {e}")
                return []
    
    @classmethod
    async def extract_album(cls, album_id: str) -> List[Dict[str, Any]]:
        """
        Extract all tracks from a Spotify album.
        
        Args:
            album_id: Spotify album ID
        
        Returns:
            List of track information with YouTube mapping
        """
        token = await cls._get_access_token()
        if not token:
            return []
        
        async with aiohttp.ClientSession() as session:
            headers = {"Authorization": f"Bearer {token}"}
            tracks = []
            url = f"https://api.spotify.com/v1/albums/{album_id}/tracks"
            
            try:
                while url:
                    async with session.get(url, headers=headers) as response:
                        if response.status != 200:
                            logger.error(f"Spotify API error: {response.status}")
                            break
                        
                        data = await response.json()
                        
                        # Get album info for artist names
                        album_url = f"https://api.spotify.com/v1/albums/{album_id}"
                        async with session.get(album_url, headers=headers) as album_response:
                            if album_response.status == 200:
                                album_data = await album_response.json()
                                artists = [artist["name"] for artist in album_data["artists"]]
                            else:
                                artists = ["Unknown"]
                        
                        for track in data["items"]:
                            search_query = f"{track['name']} {artists[0]}"
                            youtube_results = await YouTubeService.search(search_query, limit=1)
                            
                            if youtube_results:
                                result = youtube_results[0]
                                result["spotify_id"] = track["id"]
                                result["artists"] = artists
                                result["album"] = album_data.get("name", "Unknown") if 'album_data' in locals() else "Unknown"
                                result["source"] = "spotify"
                                tracks.append(result)
                            
                            await asyncio.sleep(0.1)
                        
                        url = data.get("next")
                
                return tracks
                
            except Exception as e:
                logger.error(f"Spotify album extraction failed: {e}")
                return []
    
    @classmethod
    def extract_id_from_url(cls, url: str) -> tuple:
        """
        Extract type and ID from Spotify URL.
        
        Returns:
            Tuple of (type, id) where type is 'track', 'playlist', or 'album'
        """
        if "spotify.com" not in url:
            return None, None
        
        parts = url.split("/")
        
        if "track" in parts:
            idx = parts.index("track")
            return "track", parts[idx + 1].split("?")[0]
        elif "playlist" in parts:
            idx = parts.index("playlist")
            return "playlist", parts[idx + 1].split("?")[0]
        elif "album" in parts:
            idx = parts.index("album")
            return "album", parts[idx + 1].split("?")[0]
        
        return None, None
    
    @classmethod
    async def process_url(cls, url: str) -> List[Dict[str, Any]]:
        """
        Process any Spotify URL and return track information.
        
        Args:
            url: Spotify URL (track, playlist, or album)
        
        Returns:
            List of track information dictionaries
        """
        spotify_type, spotify_id = cls.extract_id_from_url(url)
        
        if not spotify_type or not spotify_id:
            return []
        
        if spotify_type == "track":
            track = await cls.extract_track(spotify_id)
            return [track] if track else []
        elif spotify_type == "playlist":
            return await cls.extract_playlist(spotify_id)
        elif spotify_type == "album":
            return await cls.extract_album(spotify_id)
        
        return []
