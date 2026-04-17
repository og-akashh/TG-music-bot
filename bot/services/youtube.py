"""
YouTube service for searching and extracting video information.
"""

import yt_dlp
import asyncio
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class YouTubeService:
    """Service for YouTube operations."""
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
        'default_search': 'ytsearch',
        'noplaylist': True,
    }
    
    @classmethod
    async def search(cls, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search YouTube for videos.
        
        Args:
            query: Search query
            limit: Maximum number of results
        
        Returns:
            List of video information dictionaries
        """
        loop = asyncio.get_event_loop()
        
        search_opts = cls.ydl_opts.copy()
        search_opts['extract_flat'] = True
        
        try:
            with yt_dlp.YoutubeDL(search_opts) as ydl:
                # If it's already a URL, extract directly
                if "youtube.com" in query or "youtu.be" in query:
                    info = await loop.run_in_executor(
                        None, 
                        lambda: ydl.extract_info(query, download=False)
                    )
                    return [cls._format_video_info(info)]
                
                # Otherwise search
                search_query = f"ytsearch{limit}:{query}"
                info = await loop.run_in_executor(
                    None,
                    lambda: ydl.extract_info(search_query, download=False)
                )
                
                results = []
                for entry in info.get('entries', [])[:limit]:
                    if entry:
                        results.append(cls._format_video_info(entry))
                
                return results
                
        except Exception as e:
            logger.error(f"YouTube search failed: {e}")
            return []
    
    @classmethod
    async def extract_info(cls, url: str) -> Optional[Dict[str, Any]]:
        """
        Extract detailed information from a YouTube URL.
        
        Args:
            url: YouTube video URL
        
        Returns:
            Video information dictionary
        """
        loop = asyncio.get_event_loop()
        
        try:
            with yt_dlp.YoutubeDL(cls.ydl_opts) as ydl:
                info = await loop.run_in_executor(
                    None,
                    lambda: ydl.extract_info(url, download=False)
                )
                
                if 'entries' in info:  # Playlist
                    info = info['entries'][0]
                
                return cls._format_video_info(info)
                
        except Exception as e:
            logger.error(f"YouTube extraction failed: {e}")
            return None
    
    @classmethod
    async def get_playlist(cls, url: str) -> List[Dict[str, Any]]:
        """
        Extract all videos from a YouTube playlist.
        
        Args:
            url: YouTube playlist URL
        
        Returns:
            List of video information dictionaries
        """
        loop = asyncio.get_event_loop()
        
        playlist_opts = cls.ydl_opts.copy()
        playlist_opts['extract_flat'] = True
        
        try:
            with yt_dlp.YoutubeDL(playlist_opts) as ydl:
                info = await loop.run_in_executor(
                    None,
                    lambda: ydl.extract_info(url, download=False)
                )
                
                results = []
                for entry in info.get('entries', []):
                    if entry:
                        results.append(cls._format_video_info(entry))
                
                return results
                
        except Exception as e:
            logger.error(f"YouTube playlist extraction failed: {e}")
            return []
    
    @staticmethod
    def _format_video_info(info: Dict) -> Dict[str, Any]:
        """Format raw yt-dlp info into standardized structure."""
        return {
            "id": info.get("id"),
            "title": info.get("title", "Unknown Title"),
            "url": info.get("webpage_url") or f"https://youtube.com/watch?v={info.get('id')}",
            "duration": info.get("duration", 0),
            "thumbnail": info.get("thumbnail") or f"https://i.ytimg.com/vi/{info.get('id')}/hqdefault.jpg",
            "uploader": info.get("uploader", "Unknown"),
            "source": "youtube"
        }
    
    @classmethod
    async def get_video_details(cls, video_id: str) -> Optional[Dict[str, Any]]:
        """Get details for a specific video ID."""
        url = f"https://youtube.com/watch?v={video_id}"
        return await cls.extract_info(url)
    
    @classmethod
    async def get_trending(cls, region: str = "US", limit: int = 10) -> List[Dict[str, Any]]:
        """Get trending videos (requires additional setup)."""
        # This would require scraping or YouTube API
        # Placeholder implementation
        logger.warning("Trending videos not fully implemented")
        return []
