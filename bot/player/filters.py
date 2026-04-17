"""
Audio filters using FFmpeg for effects like bass boost, nightcore, etc.
"""

import subprocess
import os
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class AudioFilter:
    """Apply various audio filters using FFmpeg."""
    
    @staticmethod
    async def apply_filter(input_file: str, filter_type: str, output_file: Optional[str] = None) -> str:
        """
        Apply audio filter to input file.
        
        Args:
            input_file: Path to input audio file
            filter_type: Type of filter (bass_boost, nightcore, echo, etc.)
            output_file: Optional output path (auto-generated if None)
        
        Returns:
            Path to filtered audio file
        """
        if not output_file:
            name, ext = os.path.splitext(input_file)
            output_file = f"{name}_{filter_type}{ext}"
        
        filter_map = {
            "bass_boost": "bass=g=10:f=110",
            "nightcore": "asetrate=44100*1.25,aresample=44100,atempo=1.25",
            "echo": "aecho=0.8:0.9:1000:0.3",
            "reverb": "aecho=0.8:0.88:60:0.4",
            "flanger": "flanger",
            "tremolo": "tremolo",
            "vibrato": "vibrato=f=6.5",
            "karaoke": "stereotools=mlev=0.015625"
        }
        
        filter_str = filter_map.get(filter_type)
        if not filter_str:
            logger.warning(f"Unknown filter: {filter_type}")
            return input_file
        
        try:
            cmd = [
                "ffmpeg", "-i", input_file,
                "-af", filter_str,
                "-c:a", "libmp3lame",
                "-q:a", "2",
                "-y", output_file
            ]
            
            process = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            if process.returncode == 0:
                logger.info(f"Applied {filter_type} filter to {input_file}")
                return output_file
            else:
                logger.error(f"FFmpeg error: {process.stderr}")
                return input_file
                
        except Exception as e:
            logger.error(f"Filter application failed: {e}")
            return input_file
    
    @staticmethod
    async def change_speed(input_file: str, speed: float) -> str:
        """
        Change audio playback speed.
        
        Args:
            input_file: Path to input audio
            speed: Speed multiplier (0.5 = half speed, 2.0 = double speed)
        
        Returns:
            Path to speed-adjusted audio
        """
        name, ext = os.path.splitext(input_file)
        output_file = f"{name}_speed_{speed}{ext}"
        
        # FFmpeg atempo filter works with values between 0.5 and 2.0
        # For other values, chain multiple atempo filters
        atempo_filters = []
        remaining = speed
        
        while remaining > 2.0:
            atempo_filters.append("atempo=2.0")
            remaining /= 2.0
        
        while remaining < 0.5:
            atempo_filters.append("atempo=0.5")
            remaining /= 0.5
        
        if remaining != 1.0 or not atempo_filters:
            atempo_filters.append(f"atempo={remaining}")
        
        filter_str = ",".join(atempo_filters)
        
        try:
            cmd = [
                "ffmpeg", "-i", input_file,
                "-af", filter_str,
                "-c:a", "libmp3lame",
                "-q:a", "2",
                "-y", output_file
            ]
            
            subprocess.run(cmd, check=True, capture_output=True)
            return output_file
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Speed change failed: {e.stderr.decode()}")
            return input_file
