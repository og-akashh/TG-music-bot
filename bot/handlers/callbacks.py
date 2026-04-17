from pyrogram import Client
from pyrogram.types import CallbackQuery
from bot.player.manager import PlayerManager
from bot.player.queue import QueueManager
from bot.database import redis_client as redis
from bot.ui.keyboards import player_controls_keyboard, queue_keyboard
from bot.ui.messages import now_playing_card
import logging

logger = logging.getLogger(__name__)
player_manager: PlayerManager = None

def setup_handlers(app: Client, pm: PlayerManager):
    global player_manager
    player_manager = pm

    @app.on_callback_query()
    async def handle_callbacks(client: Client, callback: CallbackQuery):
        data = callback.data
        chat_id = callback.message.chat.id
        user_id = callback.from_user.id

        # Check if user is in voice chat or admin
        # (Add permission checks here)

        try:
            if data == "pause":
                await player_manager.pause(chat_id)
                await callback.answer("⏸ Paused")
                await update_player_message(callback)

            elif data == "resume":
                await player_manager.resume(chat_id)
                await callback.answer("▶️ Resumed")
                await update_player_message(callback)

            elif data == "skip":
                await player_manager.skip(chat_id)
                await callback.answer("⏭ Skipped")
                await callback.message.delete()

            elif data == "stop":
                await player_manager.stop(chat_id)
                await callback.answer("⏹ Stopped")
                await callback.message.delete()

            elif data == "shuffle":
                await QueueManager.shuffle(chat_id)
                await callback.answer("🔀 Queue shuffled!")

            elif data == "loop":
                modes = ["off", "single", "queue"]
                current = player_manager.loop_modes.get(chat_id, "off")
                next_mode = modes[(modes.index(current) + 1) % len(modes)]
                player_manager.set_loop_mode(chat_id, next_mode)
                await callback.answer(f"🔁 Loop: {next_mode}")

            elif data == "queue":
                queue = await QueueManager.get_queue(chat_id)
                if not queue:
                    await callback.answer("Queue is empty", show_alert=True)
                else:
                    text = format_queue_text(queue)
                    markup = queue_keyboard(len(queue) // 10 + 1)
                    await callback.message.edit_text(text, reply_markup=markup)

            elif data == "lyrics":
                current = await redis.get_current_song(chat_id)
                if current:
                    from bot.services.lyrics import LyricsService
                    lyrics = await LyricsService.fetch(current["title"])
                    if lyrics:
                        await callback.message.reply(f"**{current['title']}**\n\n{lyrics[:4000]}")
                    else:
                        await callback.answer("Lyrics not found", show_alert=True)

            elif data == "close":
                await callback.message.delete()

            elif data.startswith("vol_"):
                if data == "vol_up":
                    # Increase volume by 10
                    pass
                elif data == "vol_down":
                    # Decrease volume by 10
                    pass

            elif data.startswith("queue_page_"):
                page = int(data.split("_")[-1])
                # Handle queue pagination
                pass

            elif data == "clear_queue":
                await QueueManager.clear(chat_id)
                await callback.answer("Queue cleared!")
                await callback.message.delete()

        except Exception as e:
            logger.error(f"Callback error: {e}")
            await callback.answer("An error occurred", show_alert=True)

async def update_player_message(callback: CallbackQuery):
    """Update the now playing message with current state."""
    chat_id = callback.message.chat.id
    current = await redis.get_current_song(chat_id)
    if current:
        card = await now_playing_card(current)
        markup = player_controls_keyboard()
        try:
            await callback.message.edit_caption(
                caption=card["caption"],
                reply_markup=markup
            )
        except:
            pass

def format_queue_text(queue: list, page: int = 1, per_page: int = 10) -> str:
    """Format queue list for display."""
    start = (page - 1) * per_page
    end = start + per_page
    queue_page = queue[start:end]
    
    text = "**📋 Current Queue:**\n\n"
    for i, song in enumerate(queue_page, start + 1):
        duration = format_duration(song.get('duration', 0))
        text += f"`{i:02d}.` **{song['title']}**\n"
        text += f"     👤 {song.get('requester', 'Unknown')} | ⏱ {duration}\n"
    
    text += f"\n**Total songs:** {len(queue)}"
    return text

def format_duration(seconds: int) -> str:
    """Format duration in seconds to MM:SS or HH:MM:SS."""
    if not seconds:
        return "00:00"
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    return f"{minutes:02d}:{seconds:02d}"
