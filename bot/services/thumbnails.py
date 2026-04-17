"""
Dynamic thumbnail generator for now playing cards.
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import aiohttp
import asyncio
import os
import io
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class ThumbnailGenerator:
    """Generate dynamic thumbnails with track information."""
    
    # Configuration
    CARD_WIDTH = 800
    CARD_HEIGHT = 400
    THUMBNAIL_SIZE = 300
    FONT_PATH = "fonts/arial.ttf"  # You need to provide a font file
    CACHE_DIR = "cache/thumbnails"
    
    @classmethod
    async def generate_now_playing_card(cls, song: Dict[str, Any]) -> Optional[str]:
        """
        Generate a now playing card image.
        
        Args:
            song: Song information dictionary
        
        Returns:
            Path to generated image file
        """
        try:
            # Create cache directory
            os.makedirs(cls.CACHE_DIR, exist_ok=True)
            
            # Check cache
            cache_key = f"{song.get('id', 'unknown')}_card.png"
            cache_path = os.path.join(cls.CACHE_DIR, cache_key)
            
            if os.path.exists(cache_path):
                return cache_path
            
            # Create blank image with gradient background
            image = cls._create_gradient_background()
            draw = ImageDraw.Draw(image)
            
            # Download and paste thumbnail
            if song.get("thumbnail"):
                thumbnail = await cls._download_image(song["thumbnail"])
                if thumbnail:
                    thumbnail = cls._resize_and_round_corners(thumbnail, cls.THUMBNAIL_SIZE)
                    image.paste(thumbnail, (50, (cls.CARD_HEIGHT - cls.THUMBNAIL_SIZE) // 2))
            
            # Load fonts
            try:
                title_font = ImageFont.truetype(cls.FONT_PATH, 32)
                subtitle_font = ImageFont.truetype(cls.FONT_PATH, 24)
                small_font = ImageFont.truetype(cls.FONT_PATH, 18)
            except:
                title_font = ImageFont.load_default()
                subtitle_font = ImageFont.load_default()
                small_font = ImageFont.load_default()
            
            # Draw text information
            text_x = 400
            text_y = 100
            
            # Title
            title = song.get("title", "Unknown Title")
            title = cls._wrap_text(title, title_font, 350)
            draw.text((text_x, text_y), title, fill=(255, 255, 255), font=title_font)
            
            # Artist/Uploader
            text_y += 60
            artist = song.get("uploader") or ", ".join(song.get("artists", ["Unknown Artist"]))
            draw.text((text_x, text_y), f"🎤 {artist}", fill=(200, 200, 200), font=subtitle_font)
            
            # Duration
            text_y += 40
            duration = cls._format_duration(song.get("duration", 0))
            draw.text((text_x, text_y), f"⏱ {duration}", fill=(200, 200, 200), font=small_font)
            
            # Source
            text_y += 30
            source = song.get("source", "unknown").upper()
            draw.text((text_x, text_y), f"📡 {source}", fill=(200, 200, 200), font=small_font)
            
            # Progress bar background
            bar_y = cls.CARD_HEIGHT - 50
            draw.rectangle([50, bar_y, 750, bar_y + 10], fill=(60, 60, 60))
            
            # "Now Playing" text at top
            draw.text((50, 30), "🎵 NOW PLAYING", fill=(255, 255, 255), font=small_font)
            
            # Save image
            image.save(cache_path, "PNG")
            return cache_path
            
        except Exception as e:
            logger.error(f"Thumbnail generation failed: {e}")
            return None
    
    @staticmethod
    def _create_gradient_background() -> Image.Image:
        """Create a gradient background image."""
        image = Image.new("RGB", (800, 400), color=(20, 20, 30))
        draw = ImageDraw.Draw(image)
        
        # Create gradient
        for y in range(400):
            color = (20 + y // 10, 20 + y // 15, 30 + y // 8)
            draw.line([(0, y), (800, y)], fill=color)
        
        return image
    
    @staticmethod
    async def _download_image(url: str) -> Optional[Image.Image]:
        """Download image from URL."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.read()
                        return Image.open(io.BytesIO(data))
            return None
        except Exception as e:
            logger.error(f"Image download failed: {e}")
            return None
    
    @staticmethod
    def _resize_and_round_corners(image: Image.Image, size: int) -> Image.Image:
        """Resize image and apply rounded corners."""
        # Resize maintaining aspect ratio
        image.thumbnail((size, size), Image.Resampling.LANCZOS)
        
        # Create mask for rounded corners
        mask = Image.new("L", (size, size), 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle([(0, 0), (size, size)], radius=20, fill=255)
        
        # Apply mask
        output = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        output.paste(image.resize((size, size)), (0, 0))
        output.putalpha(mask)
        
        return output
    
    @staticmethod
    def _wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int) -> str:
        """Wrap text to fit within max width."""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            current_line.append(word)
            # Get text size using textbbox
            bbox = font.getbbox(" ".join(current_line))
            if bbox[2] - bbox[0] > max_width:
                current_line.pop()
                lines.append(" ".join(current_line))
                current_line = [word]
        
        lines.append(" ".join(current_line))
        return "\n".join(lines[:2])  # Limit to 2 lines
    
    @staticmethod
    def _format_duration(seconds: int) -> str:
        """Format duration in seconds to readable format."""
        if not seconds:
            return "00:00"
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        if hours > 0:
            return f"{hours}:{minutes:02d}:{secs:02d}"
        return f"{minutes:02d}:{secs:02d}"
    
    @classmethod
    async def generate_queue_thumbnail(cls, queue_count: int, first_song: Dict = None) -> Optional[str]:
        """Generate a thumbnail for queue display."""
        try:
            image = Image.new("RGB", (600, 200), color=(30, 30, 40))
            draw = ImageDraw.Draw(image)
            
            # Try to load font
            try:
                font = ImageFont.truetype(cls.FONT_PATH, 28)
                small_font = ImageFont.truetype(cls.FONT_PATH, 18)
            except:
                font = ImageFont.load_default()
                small_font = ImageFont.load_default()
            
            # Draw queue info
            draw.text((30, 50), f"📋 Queue: {queue_count} tracks", fill=(255, 255, 255), font=font)
            
            if first_song:
                text = f"Now: {first_song.get('title', 'Unknown')}"
                draw.text((30, 100), text, fill=(200, 200, 200), font=small_font)
            
            # Save
            path = f"{cls.CACHE_DIR}/queue_{queue_count}.png"
            image.save(path, "PNG")
            return path
            
        except Exception as e:
            logger.error(f"Queue thumbnail failed: {e}")
            return None
