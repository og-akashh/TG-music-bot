"""
Logging configuration for the bot.
"""

import logging
import sys
import os
from datetime import datetime
from typing import Optional

def setup_logger(level: str = "INFO", log_file: Optional[str] = None):
    """
    Setup logging configuration.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional custom log file path
    """
    # Create logs directory
    os.makedirs("logs", exist_ok=True)
    
    # Default log file with timestamp
    if not log_file:
        timestamp = datetime.now().strftime("%Y%m%d")
        log_file = f"logs/bot_{timestamp}.log"
    
    # Configure logging
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    # Set level
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter(log_format, date_format)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)
    
    # File handler
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(log_level)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    
    # Set specific levels for noisy libraries
    logging.getLogger("pyrogram").setLevel(logging.WARNING)
    logging.getLogger("pytgcalls").setLevel(logging.WARNING)
    logging.getLogger("yt_dlp").setLevel(logging.WARNING)
    logging.getLogger("aiohttp").setLevel(logging.WARNING)
    
    # Log startup
    logging.info("=" * 50)
    logging.info("Telegram Voice Chat Music Bot Starting...")
    logging.info(f"Log Level: {level}")
    logging.info(f"Log File: {log_file}")
    logging.info("=" * 50)

class LoggerMixin:
    """Mixin class to add logger to any class."""
    
    @property
    def logger(self):
        if not hasattr(self, '_logger'):
            self._logger = logging.getLogger(self.__class__.__name__)
        return self._logger

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(name)
