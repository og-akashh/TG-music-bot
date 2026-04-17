# 🎵 Telegram Voice Chat Music Bot

A production-grade, scalable Telegram music bot for voice chats with support for YouTube, Spotify, and more.

## ✨ Features

- 🎧 **Multi-source playback**: YouTube, Spotify, SoundCloud, direct links
- 🎛 **Advanced controls**: Pause, resume, skip, seek, volume, filters
- 📋 **Smart queue**: Shuffle, reorder, remove, persistent storage
- 🔄 **Loop modes**: Single track or entire queue
- 🎨 **Now Playing**: Dynamic cards with thumbnails
- 📝 **Lyrics**: Fetch and display song lyrics
- 🌐 **Multi-language**: i18n support
- 🔒 **Admin system**: Role-based permissions
- ⚡ **High performance**: Redis caching, async operations
- 🐳 **Docker support**: Easy deployment

## 📋 Prerequisites

- Python 3.10+
- FFmpeg
- MongoDB
- Redis
- Telegram API credentials

## 🚀 Quick Start

### Local Installation

```bash
# Clone repository
git clone https://github.com/yourusername/telegram-vc-music-bot.git
cd telegram-vc-music-bot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy and edit environment variables
cp .env.example .env
nano .env

# Run the bot
python -m bot.main
