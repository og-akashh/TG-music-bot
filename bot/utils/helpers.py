"""
Utility helper functions.
"""

import asyncio
import time
import hashlib
import re
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

def format_time(seconds: int) -> str:
    """Format seconds to HH:MM:SS or MM:SS."""
    if seconds < 0:
        seconds = 0
    
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"

def parse_time(time_str: str) -> Optional[int]:
    """Parse time string to seconds (e.g., '1h30m', '2:30', '90')."""
    time_str = time_str.lower().strip()
    
    # Check for HH:MM:SS format
    if ':' in time_str:
        parts = time_str.split(':')
        if len(parts) == 2:
            return int(parts[0]) * 60 + int(parts[1])
        elif len(parts) == 3:
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
    
    # Check for XhYmZs format
    total = 0
    pattern = r'(\d+)([dhms])'
    matches = re.findall(pattern, time_str)
    
    for value, unit in matches:
        val = int(value)
        if unit == 'd':
            total += val * 86400
        elif unit == 'h':
            total += val * 3600
        elif unit == 'm':
            total += val * 60
        elif unit == 's':
            total += val
    
    if total > 0:
        return total
    
    # Try parsing as plain seconds
    try:
        return int(time_str)
    except ValueError:
        return None

def generate_cache_key(url: str) -> str:
    """Generate a unique cache key from URL."""
    return hashlib.md5(url.encode()).hexdigest()

def clean_filename(filename: str) -> str:
    """Remove invalid characters from filename."""
    # Remove invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # Remove extra spaces
    filename = ' '.join(filename.split())
    # Limit length
    if len(filename) > 100:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        filename = name[:100] + ('.' + ext if ext else '')
    return filename

def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to max length."""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix

def extract_urls(text: str) -> List[str]:
    """Extract all URLs from text."""
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    return re.findall(url_pattern, text)

def is_youtube_url(url: str) -> bool:
    """Check if URL is from YouTube."""
    patterns = [
        r'youtube\.com',
        r'youtu\.be',
        r'm\.youtube\.com'
    ]
    return any(re.search(pattern, url.lower()) for pattern in patterns)

def is_spotify_url(url: str) -> bool:
    """Check if URL is from Spotify."""
    return 'spotify.com' in url.lower()

def is_soundcloud_url(url: str) -> bool:
    """Check if URL is from SoundCloud."""
    return 'soundcloud.com' in url.lower()

def extract_youtube_id(url: str) -> Optional[str]:
    """Extract YouTube video ID from URL."""
    patterns = [
        r'(?:youtube\.com/watch\?v=)([\w-]+)',
        r'(?:youtu\.be/)([\w-]+)',
        r'(?:youtube\.com/embed/)([\w-]+)',
        r'(?:m\.youtube\.com/watch\?v=)([\w-]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def format_file_size(size_bytes: int) -> str:
    """Format file size in bytes to human readable format."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"

def get_timestamp() -> int:
    """Get current Unix timestamp."""
    return int(time.time())

def format_timestamp(timestamp: int, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format Unix timestamp to readable date."""
    dt = datetime.fromtimestamp(timestamp)
    return dt.strftime(format_str)

def time_ago(timestamp: int) -> str:
    """Get human readable time difference."""
    now = datetime.now()
    past = datetime.fromtimestamp(timestamp)
    diff = now - past
    
    if diff.days > 365:
        years = diff.days // 365
        return f"{years} year{'s' if years != 1 else ''} ago"
    elif diff.days > 30:
        months = diff.days // 30
        return f"{months} month{'s' if months != 1 else ''} ago"
    elif diff.days > 0:
        return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    else:
        return "just now"

async def retry_async(func, max_retries: int = 3, delay: float = 1.0):
    """Retry an async function on failure."""
    for attempt in range(max_retries):
        try:
            return await func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            logger.warning(f"Retry {attempt + 1}/{max_retries} after error: {e}")
            await asyncio.sleep(delay * (attempt + 1))

def chunk_list(lst: List, chunk_size: int) -> List[List]:
    """Split list into chunks."""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

def merge_dicts(dict1: Dict, dict2: Dict) -> Dict:
    """Deep merge two dictionaries."""
    result = dict1.copy()
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = value
    return result

def sanitize_html(text: str) -> str:
    """Sanitize HTML tags from text."""
    import html
    return html.escape(text)
