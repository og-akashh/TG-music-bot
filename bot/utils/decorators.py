"""
Decorators for permission checks and rate limiting.
"""

from functools import wraps
from typing import Callable, Dict
import asyncio
import time
from pyrogram.types import Message, CallbackQuery
from pyrogram.errors import RPCError
from bot.database.mongo import chats
import logging

logger = logging.getLogger(__name__)

# Simple in-memory rate limiter
_rate_limits: Dict[int, Dict[str, list]] = {}

def rate_limit(max_calls: int = 5, time_window: int = 60):
    """
    Rate limit decorator for handlers.
    
    Args:
        max_calls: Maximum number of calls allowed in time window
        time_window: Time window in seconds
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(client, update, *args, **kwargs):
            # Get user ID
            if isinstance(update, Message):
                user_id = update.from_user.id
            elif isinstance(update, CallbackQuery):
                user_id = update.from_user.id
            else:
                return await func(client, update, *args, **kwargs)
            
            current_time = time.time()
            
            # Initialize rate limit tracking
            if user_id not in _rate_limits:
                _rate_limits[user_id] = {}
            
            command = func.__name__
            if command not in _rate_limits[user_id]:
                _rate_limits[user_id][command] = []
            
            # Clean old timestamps
            _rate_limits[user_id][command] = [
                ts for ts in _rate_limits[user_id][command]
                if current_time - ts < time_window
            ]
            
            # Check rate limit
            if len(_rate_limits[user_id][command]) >= max_calls:
                remaining = time_window - (current_time - _rate_limits[user_id][command][0])
                if isinstance(update, Message):
                    await update.reply(f"⏳ Rate limited. Please wait {remaining:.0f} seconds.")
                elif isinstance(update, CallbackQuery):
                    await update.answer(f"Please wait {remaining:.0f} seconds", show_alert=True)
                return
            
            # Add current timestamp
            _rate_limits[user_id][command].append(current_time)
            
            return await func(client, update, *args, **kwargs)
        return wrapper
    return decorator

def admin_only(func: Callable):
    """
    Decorator to restrict command to admins only.
    """
    @wraps(func)
    async def wrapper(client, update: Message, *args, **kwargs):
        chat_id = update.chat.id
        user_id = update.from_user.id
        
        # Check if private chat
        if update.chat.type == "private":
            return await func(client, update, *args, **kwargs)
        
        # Check if user is admin
        try:
            member = await client.get_chat_member(chat_id, user_id)
            if member.status in ["creator", "administrator"]:
                return await func(client, update, *args, **kwargs)
        except RPCError as e:
            logger.error(f"Failed to check admin status: {e}")
        
        await update.reply("⚠️ This command is for admins only.")
        return
    return wrapper

def owner_only(func: Callable):
    """
    Decorator to restrict command to bot owner only.
    """
    @wraps(func)
    async def wrapper(client, update: Message, *args, **kwargs):
        from bot.config import settings
        
        user_id = update.from_user.id
        if user_id == settings.OWNER_ID:
            return await func(client, update, *args, **kwargs)
        
        await update.reply("⚠️ This command is for the bot owner only.")
        return
    return wrapper

def group_only(func: Callable):
    """
    Decorator to restrict command to groups only.
    """
    @wraps(func)
    async def wrapper(client, update: Message, *args, **kwargs):
        if update.chat.type in ["group", "supergroup"]:
            return await func(client, update, *args, **kwargs)
        
        await update.reply("⚠️ This command only works in groups.")
        return
    return wrapper

def require_voice_chat(func: Callable):
    """
    Decorator to check if bot is in voice chat.
    """
    @wraps(func)
    async def wrapper(client, update: Message, *args, **kwargs):
        from bot.player.manager import player_manager
        
        chat_id = update.chat.id
        if chat_id in player_manager.active_players:
            return await func(client, update, *args, **kwargs)
        
        await update.reply("⚠️ Bot is not in voice chat. Use /play to start.")
        return
    return wrapper

def catch_errors(func: Callable):
    """
    Decorator to catch and log errors.
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}", exc_info=True)
            # Try to notify user if possible
            try:
                update = args[1] if len(args) > 1 else None
                if isinstance(update, Message):
                    await update.reply(f"❌ An error occurred: {str(e)[:100]}")
                elif isinstance(update, CallbackQuery):
                    await update.answer("An error occurred", show_alert=True)
            except:
                pass
            return None
    return wrapper

def require_arg(arg_name: str, error_message: str = None):
    """
    Decorator to require a command argument.
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(client, update: Message, *args, **kwargs):
            if len(update.command) < 2:
                msg = error_message or f"⚠️ Please provide {arg_name}"
                await update.reply(msg)
                return
            return await func(client, update, *args, **kwargs)
        return wrapper
    return decorator

def throttle(seconds: int = 2):
    """
    Throttle decorator to prevent spam.
    """
    _last_called = {}
    
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(client, update, *args, **kwargs):
            user_id = update.from_user.id
            current_time = time.time()
            
            if user_id in _last_called:
                elapsed = current_time - _last_called[user_id]
                if elapsed < seconds:
                    await asyncio.sleep(seconds - elapsed)
            
            _last_called[user_id] = current_time
            return await func(client, update, *args, **kwargs)
        return wrapper
    return decorator
