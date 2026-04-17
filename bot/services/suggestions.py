"""
Smart suggestion service for auto-play related songs.
"""

from typing import List, Dict, Any, Optional
from bot.services.youtube import YouTubeService
import random
import logging

logger = logging.getLogger(__name__)

class SuggestionService:
    """Service for generating smart song suggestions."""
    
    @classmethod
    async def get_related_songs(cls, current_song: Dict[str, Any], limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get related songs based on current playing track.
        
        Args:
            current_song: Current song information
            limit: Maximum number of suggestions
        
        Returns:
            List of suggested songs
        """
        suggestions = []
        
        # Strategy 1: Search by title keywords
        if current_song.get("title"):
            keywords = cls._extract_keywords(current_song["title"])
            for keyword in keywords[:3]:
                results = await YouTubeService.search(keyword, limit=2)
                suggestions.extend(results)
        
        # Strategy 2: Search by artist + similar
        if current_song.get("uploader"):
            artist = current_song["uploader"]
            # Search for more songs by same artist
            artist_results = await YouTubeService.search(f"{artist} songs", limit=3)
            suggestions.extend(artist_results)
            
            # Search for similar artists (simplified)
            similar_results = await YouTubeService.search(f"similar to {artist}", limit=2)
            suggestions.extend(similar_results)
        
        # Remove duplicates and current song
        unique_suggestions = []
        seen_ids = {current_song.get("id")}
        
        for song in suggestions:
            if song.get("id") not in seen_ids and len(unique_suggestions) < limit:
                seen_ids.add(song.get("id"))
                unique_suggestions.append(song)
        
        # If not enough, add trending/popular
        if len(unique_suggestions) < limit:
            trending = await cls._get_trending_songs(limit - len(unique_suggestions))
            for song in trending:
                if song.get("id") not in seen_ids:
                    unique_suggestions.append(song)
        
        return unique_suggestions[:limit]
    
    @staticmethod
    def _extract_keywords(text: str) -> List[str]:
        """Extract meaningful keywords from text."""
        # Remove common words and punctuation
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
        
        # Clean text
        import re
        words = re.findall(r'\w+', text.lower())
        
        # Filter stop words and short words
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        
        # Return unique keywords
        return list(dict.fromkeys(keywords))
    
    @classmethod
    async def _get_trending_songs(cls, limit: int = 5) -> List[Dict[str, Any]]:
        """Get trending/popular songs."""
        # Simplified: Search for popular music
        trending_queries = [
            "top hits 2024",
            "popular songs",
            "trending music",
            "viral songs"
        ]
        
        query = random.choice(trending_queries)
        results = await YouTubeService.search(query, limit=limit)
        
        return results
    
    @classmethod
    async def get_similar_artist_songs(cls, artist: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get more songs by similar artists."""
        # Search for similar artists and their songs
        query = f"music similar to {artist}"
        results = await YouTubeService.search(query, limit=limit)
        return results
    
    @classmethod
    async def get_genre_based_suggestions(cls, genre: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get suggestions based on genre."""
        query = f"{genre} music playlist"
        results = await YouTubeService.search(query, limit=limit)
        return results
    
    @classmethod
    async def get_mood_based_suggestions(cls, mood: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get suggestions based on mood."""
        mood_queries = {
            "happy": "upbeat happy songs",
            "sad": "emotional sad songs",
            "relaxed": "calm relaxing music",
            "energetic": "energetic workout music",
            "romantic": "romantic love songs"
        }
        
        query = mood_queries.get(mood.lower(), f"{mood} music")
        results = await YouTubeService.search(query, limit=limit)
        return results
    
    @classmethod
    async def auto_queue_suggestions(cls, chat_id: int, current_song: Dict[str, Any], queue_count: int):
        """
        Automatically add suggestions to queue when it's running low.
        
        Args:
            chat_id: Chat ID
            current_song: Current playing song
            queue_count: Current number of songs in queue
        """
        from bot.player.queue import QueueManager
        
        # Only auto-add if queue is below threshold
        if queue_count >= 3:
            return
        
        suggestions = await cls.get_related_songs(current_song, limit=5 - queue_count)
        
        if suggestions:
            await QueueManager.add_many(chat_id, suggestions)
            logger.info(f"Auto-added {len(suggestions)} suggestions to queue for chat {chat_id}")
