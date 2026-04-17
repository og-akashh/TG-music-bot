"""
Formatted messages and cards for bot responses.
"""

from typing import Dict, Any, Optional
from bot.services.thumbnails import ThumbnailGenerator
import logging

logger = logging.getLogger(__name__)

async def now_playing_card(song: Dict[str, Any]) -> Dict[str, str]:
    """
    Generate a now playing card with thumbnail and caption.
    
    Args:
        song: Song information dictionary
    
    Returns:
        Dictionary with 'thumbnail' path and 'caption' text
    """
    # Generate thumbnail
    thumbnail_path = await ThumbnailGenerator.generate_now_playing_card(song)
    
    # Format caption
    title = song.get("title", "Unknown Title")
    artist = song.get("uploader") or ", ".join(song.get("artists", ["Unknown Artist"]))
    duration = format_duration(song.get("duration", 0))
    source = song.get("source", "unknown").upper()
    requester = song.get("requested_by_name", "Unknown")
    
    caption = f"""
**🎵 Now Playing**

**{title}**
🎤 {artist}

⏱ Duration: `{duration}`
📡 Source: `{source}`
👤 Requested by: {requester}

Use buttons below to control playback:
"""
    
    return {
        "thumbnail": thumbnail_path,
        "caption": caption
    }

def format_duration(seconds: int) -> str:
    """Format duration to readable string."""
    if not seconds:
        return "00:00"
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"

def queue_message(queue: list, page: int = 1, per_page: int = 10) -> str:
    """Format queue list message."""
    if not queue:
        return "📭 **Queue is empty**\n\nUse `/play` to add songs!"
    
    start = (page - 1) * per_page
    end = start + per_page
    queue_page = queue[start:end]
    
    total_duration = sum(song.get('duration', 0) for song in queue)
    
    text = "**📋 Queue List**\n\n"
    
    for i, song in enumerate(queue_page, start + 1):
        title = song.get("title", "Unknown")
        duration = format_duration(song.get("duration", 0))
        requester = song.get("requested_by_name", "Unknown")
        
        text += f"`{i:02d}.` **{title}**\n"
        text += f"     ⏱ `{duration}` | 👤 {requester}\n"
    
    text += f"\n**📊 Queue Stats:**"
    text += f"\n• Total Songs: `{len(queue)}`"
    text += f"\n• Total Duration: `{format_duration(total_duration)}`"
    
    if len(queue) > per_page:
        text += f"\n\n📄 Page {page}/{(len(queue) - 1) // per_page + 1}"
    
    return text

def lyrics_message(title: str, artist: str, lyrics: str) -> str:
    """Format lyrics message."""
    header = f"**📝 Lyrics for:** {title}\n"
    if artist:
        header += f"**🎤 Artist:** {artist}\n"
    header += "\n" + "─" * 30 + "\n\n"
    
    # Truncate if too long (Telegram has 4096 char limit)
    max_length = 4000 - len(header)
    if len(lyrics) > max_length:
        lyrics = lyrics[:max_length] + "\n\n... (truncated)"
    
    return header + lyrics

def help_message() -> str:
    """Generate help message."""
    return """
**🎵 Music Bot Commands**

**Playback Controls:**
`/play <query>` - Play or queue a song
`/pause` - Pause current track
`/resume` - Resume playback
`/skip` - Skip to next song
`/stop` - Stop and clear queue
`/seek <seconds>` - Seek position
`/volume <0-200>` - Adjust volume
`/loop` - Toggle loop mode

**Queue Management:**
`/queue` - Show current queue
`/shuffle` - Shuffle queue
`/clearqueue` - Clear all songs
`/remove <index>` - Remove song

**Information:**
`/now` - Currently playing
`/lyrics` - Fetch lyrics
`/history` - Recent tracks

**Admin Commands:**
`/settings` - Bot settings
`/admin` - Admin panel

**Tips:**
• Support YouTube & Spotify links
• Use inline buttons for quick controls
• Bot auto-plays next song

*Made with ❤️ using Pyrogram*
"""

def error_message(error: str) -> str:
    """Format error message."""
    return f"❌ **Error:** {error}"

def success_message(text: str) -> str:
    """Format success message."""
    return f"✅ {text}"

def info_message(text: str) -> str:
    """Format info message."""
    return f"ℹ️ {text}"

def warning_message(text: str) -> str:
    """Format warning message."""
    return f"⚠️ {text}"
