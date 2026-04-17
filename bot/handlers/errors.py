from pyrogram import Client
from pyrogram.errors import FloodWait, RPCError
import asyncio
import logging

logger = logging.getLogger(__name__)

def setup_handlers(app: Client):
    """Setup error handlers."""
    
    @app.on_error()
    async def error_handler(client: Client, error: Exception):
        """Handle all uncaught exceptions."""
        if isinstance(error, FloodWait):
            logger.warning(f"Flood wait: {error.value} seconds")
            await asyncio.sleep(error.value + 1)
        elif isinstance(error, RPCError):
            logger.error(f"RPC Error: {error}")
        else:
            logger.error(f"Unexpected error: {error}", exc_info=True)
