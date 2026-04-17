"""
Lyrics fetching service from multiple sources.
"""

import aiohttp
import re
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class LyricsService:
    """Service for fetching song lyrics."""
    
    @classmethod
    async def fetch(cls, query: str, artist: str = None) -> Optional[str]:
        """
        Fetch lyrics for a song.
        
        Args:
            query: Song title
            artist: Optional artist name
        
        Returns:
            Lyrics as string or None if not found
        """
        # Clean query
        query = cls._clean_query(query)
        if artist:
            artist = cls._clean_query(artist)
            full_query = f"{artist} {query}"
        else:
            full_query = query
        
        # Try multiple sources
        lyrics = await cls._fetch_from_musixmatch(full_query)
        if lyrics:
            return lyrics
        
        lyrics = await cls._fetch_from_azlyrics(query, artist)
        if lyrics:
            return lyrics
        
        lyrics = await cls._fetch_from_genius(query, artist)
        if lyrics:
            return lyrics
        
        return None
    
    @staticmethod
    def _clean_query(text: str) -> str:
        """Remove special characters and extra spaces."""
        # Remove text in parentheses and brackets
        text = re.sub(r'\([^)]*\)', '', text)
        text = re.sub(r'\[[^\]]*\]', '', text)
        # Remove special characters
        text = re.sub(r'[^\w\s]', '', text)
        # Remove extra spaces
        text = ' '.join(text.split())
        return text.lower()
    
    @classmethod
    async def _fetch_from_musixmatch(cls, query: str) -> Optional[str]:
        """Fetch lyrics from Musixmatch (unofficial API)."""
        try:
            # This is a simplified example - in production you'd need proper API or scraping
            search_url = f"https://www.musixmatch.com/search/{query.replace(' ', '%20')}"
            
            async with aiohttp.ClientSession() as session:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                }
                async with session.get(search_url, headers=headers) as response:
                    if response.status == 200:
                        html = await response.text()
                        # Simple regex to extract lyrics (would need more robust parsing)
                        match = re.search(r'"lyrics"\s*:\s*"([^"]+)"', html)
                        if match:
                            lyrics = match.group(1)
                            lyrics = lyrics.replace('\\n', '\n').replace('\\"', '"')
                            return lyrics
            return None
        except Exception as e:
            logger.error(f"Musixmatch fetch failed: {e}")
            return None
    
    @classmethod
    async def _fetch_from_azlyrics(cls, title: str, artist: str = None) -> Optional[str]:
        """Fetch lyrics from AZLyrics."""
        if not artist:
            return None
        
        try:
            # Format for AZLyrics URL
            artist_clean = re.sub(r'[^\w]', '', artist.lower())
            title_clean = re.sub(r'[^\w]', '', title.lower())
            
            url = f"https://www.azlyrics.com/lyrics/{artist_clean}/{title_clean}.html"
            
            async with aiohttp.ClientSession() as session:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                }
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        html = await response.text()
                        # Extract lyrics between specific divs
                        match = re.search(
                            r'<!-- Usage of azlyrics\.com content.*?-->(.*?)</div>',
                            html,
                            re.DOTALL
                        )
                        if match:
                            lyrics = match.group(1)
                            lyrics = re.sub(r'<br\s*/?>', '\n', lyrics)
                            lyrics = re.sub(r'<[^>]+>', '', lyrics)
                            return lyrics.strip()
            return None
        except Exception as e:
            logger.error(f"AZLyrics fetch failed: {e}")
            return None
    
    @classmethod
    async def _fetch_from_genius(cls, title: str, artist: str = None) -> Optional[str]:
        """Fetch lyrics from Genius (unofficial)."""
        try:
            search_query = f"{title} {artist}" if artist else title
            search_url = f"https://genius.com/api/search?q={search_query.replace(' ', '%20')}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(search_url) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Get first result
                        hits = data.get("response", {}).get("hits", [])
                        if hits:
                            song_url = hits[0]["result"]["url"]
                            
                            # Fetch lyrics page
                            async with session.get(song_url) as lyric_response:
                                if lyric_response.status == 200:
                                    html = await lyric_response.text()
                                    
                                    # Extract lyrics
                                    match = re.search(
                                        r'<div[^>]*data-lyrics-container[^>]*>(.*?)</div>',
                                        html,
                                        re.DOTALL
                                    )
                                    if match:
                                        lyrics = match.group(1)
                                        lyrics = re.sub(r'<br\s*/?>', '\n', lyrics)
                                        lyrics = re.sub(r'<[^>]+>', '', lyrics)
                                        return lyrics.strip()
            return None
        except Exception as e:
            logger.error(f"Genius fetch failed: {e}")
            return None
    
    @classmethod
    async def get_synced_lyrics(cls, query: str) -> Optional[list]:
        """
        Get time-synced lyrics (LRC format).
        
        Returns:
            List of (timestamp, text) tuples or None
        """
        # This would require specific APIs or sources with LRC files
        # Placeholder for future implementation
        return None
