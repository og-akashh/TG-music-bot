# 🎵 Telegram Voice Chat Music Bot

<div align="center">

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.10+-green.svg)
![License](https://img.shields.io/badge/license-MIT-yellow.svg)
![Docker](https://img.shields.io/badge/docker-ready-brightgreen.svg)

A production-grade, highly scalable Telegram music bot for voice chats with support for YouTube, Spotify, SoundCloud, and more.

[Features](#-features) • [Installation](#-installation) • [Configuration](#-configuration) • [Commands](#-commands) • [Deployment](#-deployment) • [Troubleshooting](#-troubleshooting)

</div>

---

## 📋 Table of Contents

- [Features](#-features)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
  - [Local Installation](#local-installation)
  - [Docker Installation](#docker-installation)
- [Configuration](#-configuration)
- [Commands](#-commands)
- [Architecture](#-architecture)
- [Deployment](#-deployment)
  - [VPS Deployment](#vps-deployment)
  - [Cloud Platforms](#cloud-platforms)
- [Troubleshooting](#-troubleshooting)
- [FAQ](#-faq)
- [Contributing](#-contributing)
- [License](#-license)
- [Support](#-support)

---

## ✨ Features

### 🎧 Core Functionality
- **Multi-Source Playback**
  - YouTube (links + search)
  - Spotify (tracks, playlists, albums via API)
  - SoundCloud
  - Direct audio links
  - Local server files

- **Smart Queue System**
  - Add, remove, shuffle, reorder tracks
  - Auto-play next song
  - Persistent queue (Redis + MongoDB backup)
  - Queue history

- **Advanced Playback Controls**
  - Play/Pause/Resume/Stop/Skip
  - Seek forward/backward
  - Loop modes (off/single/queue)
  - Real-time volume control (0-200%)

### 🎛 Advanced Features
- **Auto-reconnect**: Automatically rejoin if voice chat ends
- **Multi-chat Support**: Handle multiple groups simultaneously
- **Admin Control System**: Role-based permissions (owner/admin/user)
- **Interactive UI**: Inline keyboards for easy control
- **Now Playing Cards**: Dynamic thumbnails with track info
- **Lyrics Fetching**: Multi-source lyrics (Genius, AZLyrics, Musixmatch)
- **Audio Filters**: Bass boost, nightcore, echo, reverb, and more
- **Smart Caching**: Optimized yt-dlp caching system
- **Auto-suggestions**: Smart related song recommendations
- **Multi-language**: i18n system for multiple languages
- **Comprehensive Logging**: Detailed logging and monitoring

### 🔒 Security Features
- Environment variable configuration
- Input validation and sanitization
- Rate limiting protection
- Exception handling with fail-safe recovery
- Secure session management

---

## 📦 Prerequisites

### System Requirements
- **Python**: 3.10 or higher
- **FFmpeg**: Latest version
- **MongoDB**: 5.0+ (local or Atlas)
- **Redis**: 6.0+
- **RAM**: Minimum 512MB (2GB recommended)
- **Storage**: 1GB+ for cache

### API Credentials
- **Telegram API**: Get from [my.telegram.org](https://my.telegram.org)
  - `API_ID`
  - `API_HASH`
  - `BOT_TOKEN` (from [@BotFather](https://t.me/BotFather))
- **Spotify API** (Optional): Get from [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
  - `SPOTIFY_CLIENT_ID`
  - `SPOTIFY_CLIENT_SECRET`

---

## 🚀 Installation

### Local Installation

#### Step 1: Clone Repository
```bash
git clone https://github.com/yourusername/telegram-vc-music-bot.git
cd telegram-vc-music-bot
```
### Step 2: Install System Dependencies
#### Ubuntu/Debian:

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv ffmpeg redis-server
```
### Install MongoDB
curl -fsSL https://www.mongodb.org/static/pgp/server-7.0.asc | sudo gpg --dearmor -o /usr/share/keyrings/mongodb-server-7.0.gpg
echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list
sudo apt update
sudo apt install -y mongodb-org
sudo systemctl start mongod redis-server
sudo systemctl enable mongod redis-server
### macOS:
```bash
brew install python3 ffmpeg redis mongodb-community
brew services start redis mongodb-community
```
### Windows:

Install Python from python.org

Install FFmpeg from ffmpeg.org

Install MongoDB from mongodb.com

Install Redis from redis.io or use WSL

### Step 3: Setup Python Environment
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip

# Install Python dependencies
pip install -r requirements.txt
```
### Step 4: Configure Environment
```bash
# Copy example environment file
cp .env.example .env

# Edit with your credentials
nano .env  # or use your preferred editor
```
### Step 5: Generate Silence Audio File
```bash
# Using FFmpeg
ffmpeg -f lavfi -i anullsrc=r=44100:cl=mono -t 1 -q:a 9 -acodec libmp3lame silence.mp3
```
### Step 6: Run the Bot
```bash
# Create necessary directories
mkdir -p downloads logs cache

# Run the bot
python -m bot.main
```
## Docker Installation
### Using Docker Compose (Recommended)
```bash
# Clone repository
git clone https://github.com/yourusername/telegram-vc-music-bot.git
cd telegram-vc-music-bot

# Copy and edit environment file
cp .env.example .env
nano .env

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f bot

# Stop services
docker-compose down
```
#### Using Docker Directly
```bash
# Build image
docker build -t telegram-music-bot .

# Run container
docker run -d \
  --name music-bot \
  --env-file .env \
  -v $(pwd)/downloads:/app/downloads \
  -v $(pwd)/logs:/app/logs \
  --restart unless-stopped \
  telegram-music-bot
```
## ⚙️ Configuration
### Environment Variables
##### Create a .env file with the following variables:

```env
# ============================================
# TELEGRAM API CREDENTIALS (Required)
# ============================================
# Get from https://my.telegram.org
API_ID=1234567
API_HASH=your_api_hash_here

# Get from @BotFather on Telegram
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz

# Pyrogram session string (generated automatically)
SESSION_STRING=

# ============================================
# DATABASE CONFIGURATION (Required)
# ============================================
# MongoDB connection
MONGO_URI=mongodb://localhost:27017
MONGO_DB_NAME=telegram_music_bot

# Redis connection
REDIS_URL=redis://localhost:6379/0

# ============================================
# SPOTIFY API (Optional)
# ============================================
# Get from https://developer.spotify.com/dashboard
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret

# ============================================
# BOT SETTINGS
# ============================================
# Your Telegram user ID (get from @userinfobot)
OWNER_ID=1234567890

# Maximum songs in queue
MAX_QUEUE_SIZE=50

# Maximum song duration in seconds (3600 = 1 hour)
MAX_SONG_DURATION=3600

# Auto-leave empty voice chat after X seconds
AUTO_LEAVE_EMPTY=300

# Auto-rejoin if voice chat restarts
AUTO_REJOIN=true

# Logging level (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL=INFO

# Default language (en, es, fr, de, etc.)
LANGUAGE=en

# ============================================
# SECURITY SETTINGS
# ============================================
# Rate limit per user (messages per minute)
RATE_LIMIT=60

# Allowed update types
ALLOWED_UPDATES=["message", "callback_query", "chat_member"]

# ============================================
# PATHS
# ============================================
DOWNLOAD_DIR=downloads
LOG_DIR=logs
CACHE_DIR=cache
```
### Getting Your Telegram API Credentials
#### API_ID and API_HASH:

Go to my.telegram.org

Log in with your phone number

Go to "API Development Tools"

Create a new application

Copy api_id and api_hash

#### BOT_TOKEN:

Open Telegram and search for @BotFather

Send /newbot command

Follow the instructions

Copy the bot token provided

#### OWNER_ID:

Search for @userinfobot on Telegram

Start the bot and send any message

Copy your numeric ID

Getting Spotify API Credentials (Optional)
Go to Spotify Developer Dashboard

Log in with your Spotify account

Click "Create App"

Fill in app name and description

Copy Client ID and Client Secret

Click "Edit Settings" and add http://localhost:8888/callback to Redirect URIs

### 📚 Commands
### 🎵 Playback Commands
#### Command	Description	Example
/play <query>	Play or queue a song	/play Despacito
/play <url>	Play from URL	/play https://youtu.be/...
/pause	Pause current track	/pause
/resume	Resume playback	/resume
/skip	Skip to next song	/skip
/stop	Stop and clear queue	/stop
/seek <seconds>	Seek forward/backward	/seek 30 or /seek -10
/volume <0-200>	Adjust volume	/volume 150
/loop	Toggle loop mode	/loop
#### 📋 Queue Management
##### Command	Description	Example
/queue	Show current queue	/queue
/shuffle	Shuffle the queue	/shuffle
/clearqueue	Clear all songs	/clearqueue
/remove <index>	Remove song from queue	/remove 3
/move <from> <to>	Move song in queue	/move 2 5
#### ℹ️ Information Commands
##### Command	Description	Example
/now	Show currently playing	/now
/lyrics	Fetch lyrics	/lyrics
/history	Show recent tracks	/history
/songinfo	Detailed song info	/songinfo
#### 🎨 Audio Filters
##### Command	Description	Example
/filter bass	Apply bass boost	/filter bass
/filter nightcore	Nightcore effect	/filter nightcore
/filter echo	Echo effect	/filter echo
/filter reverb	Reverb effect	/filter reverb
/filter off	Remove all filters	/filter off
#### ⚙️ Admin Commands
##### Command	Description	Example
/settings	Bot settings panel	/settings
/admin	Admin control panel	/admin
/ban <user>	Ban user from bot	/ban @username
/unban <user>	Unban user	/unban @username
/stats	Bot statistics	/stats
/broadcast	Broadcast message	/broadcast Hello everyone!
### 🎮 Inline Controls
##### The bot features an interactive inline keyboard for easy control:

```text
┌─────────────────────────────────┐
│  ⏮  │  ⏸  │  ▶️  │  ⏭  │  🔁  │
├─────────────────────────────────┤
│  🔀  │  📋  │  ⏹  │  🔊  │  🔉  │
├─────────────────────────────────┤
│         📝 Lyrics  │  ❌ Close   │
└─────────────────────────────────┘
```
### 🏗️ Architecture
#### Project Structure
```text
telegram_vc_music_bot/
├── bot/
│   ├── __init__.py
│   ├── main.py                 # Application entry point
│   ├── config.py               # Configuration management
│   │
│   ├── database/               # Database layer
│   │   ├── __init__.py
│   │   ├── mongo.py            # MongoDB operations
│   │   └── redis_client.py     # Redis cache & queue
│   │
│   ├── handlers/               # Event handlers
│   │   ├── __init__.py
│   │   ├── commands.py         # Command handlers
│   │   ├── callbacks.py        # Inline button callbacks
│   │   └── errors.py           # Error handling
│   │
│   ├── player/                 # Core player logic
│   │   ├── __init__.py
│   │   ├── manager.py          # Player management
│   │   ├── queue.py            # Queue management
│   │   ├── voice_client.py     # PyTgCalls wrapper
│   │   ├── downloader.py       # yt-dlp integration
│   │   └── filters.py          # FFmpeg audio filters
│   │
│   ├── services/               # External services
│   │   ├── __init__.py
│   │   ├── youtube.py          # YouTube API
│   │   ├── spotify.py          # Spotify API
│   │   ├── lyrics.py           # Lyrics fetching
│   │   ├── thumbnails.py       # Image generation
│   │   └── suggestions.py      # Auto-suggestions
│   │
│   ├── ui/                     # User interface
│   │   ├── __init__.py
│   │   ├── keyboards.py        # Inline keyboards
│   │   └── messages.py         # Formatted messages
│   │
│   └── utils/                  # Utilities
│       ├── __init__.py
│       ├── helpers.py          # Helper functions
│       ├── logger.py           # Logging setup
│       └── decorators.py       # Custom decorators
│
├── downloads/                  # Audio cache directory
├── logs/                       # Log files directory
├── cache/                      # Thumbnail cache
│
├── .env.example                # Environment template
├── .gitignore                  # Git ignore rules
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Docker configuration
├── docker-compose.yml          # Docker Compose config
├── deploy.sh                   # Deployment script
├── silence.mp3                 # Silent audio file
└── README.md                   # This file
```
#### Data Flow
```text
User Command → Handler → Service → Player → Voice Chat
     ↓            ↓          ↓         ↓
   Queue ← → Redis Cache → MongoDB (persistence)
     ↓
  Downloader → yt-dlp → FFmpeg → Audio Stream
```
### Technology Stack
Layer	Technology	Purpose
Bot Framework	Pyrogram 2.3+	Telegram MTProto API
Voice Calls	Py-TgCalls 2.0+	Voice chat streaming
Media Download	yt-dlp	Audio extraction
Database	MongoDB + Motor	Persistent storage
Cache	Redis 5.0+	Queue & session cache
Audio Processing	FFmpeg	Format conversion & filters
Async Runtime	asyncio + uvloop	High-performance async
HTTP Client	aiohttp	Async HTTP requests
Image Processing	Pillow	Thumbnail generation
🚢 Deployment
VPS Deployment
Option 1: Automatic Deployment Script
bash
# Download deployment script
wget https://raw.githubusercontent.com/yourusername/telegram-vc-music-bot/main/deploy.sh

# Make it executable
chmod +x deploy.sh

# Run deployment
./deploy.sh
Option 2: Manual VPS Setup (Ubuntu 22.04)
bash
# 1. Update system
sudo apt update && sudo apt upgrade -y

# 2. Install dependencies
sudo apt install -y python3-pip python3-venv ffmpeg redis-server mongodb git

# 3. Start services
sudo systemctl start mongodb redis-server
sudo systemctl enable mongodb redis-server

# 4. Clone repository
git clone https://github.com/yourusername/telegram-vc-music-bot.git
cd telegram-vc-music-bot

# 5. Setup Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 6. Configure environment
cp .env.example .env
nano .env  # Edit with your credentials

# 7. Create systemd service
sudo nano /etc/systemd/system/telegram-music-bot.service
Systemd Service File:

ini
[Unit]
Description=Telegram VC Music Bot
After=network.target mongodb.service redis-server.service
Wants=mongodb.service redis-server.service

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/telegram-vc-music-bot
Environment="PATH=/home/ubuntu/telegram-vc-music-bot/venv/bin"
ExecStart=/home/ubuntu/telegram-vc-music-bot/venv/bin/python -m bot.main
Restart=on-failure
RestartSec=10
StandardOutput=append:/home/ubuntu/telegram-vc-music-bot/logs/bot.log
StandardError=append:/home/ubuntu/telegram-vc-music-bot/logs/error.log

[Install]
WantedBy=multi-user.target
bash
# 8. Start the service
sudo systemctl daemon-reload
sudo systemctl enable telegram-music-bot
sudo systemctl start telegram-music-bot

# 9. Check status
sudo systemctl status telegram-music-bot
sudo journalctl -u telegram-music-bot -f
Cloud Platforms
Deploy on Render
Fork the repository to your GitHub account

Go to Render and create account

Click "New +" → "Web Service"

Connect your GitHub repository

Configure:

Name: telegram-music-bot

Environment: Docker

Branch: main

Add environment variables from .env.example

Click "Create Web Service"

Deploy on Railway
bash
# 1. Install Railway CLI
npm i -g @railway/cli

# 2. Login
railway login

# 3. Initialize project
railway init

# 4. Deploy
railway up

# 5. Add environment variables
railway variables set API_ID=your_api_id
railway variables set API_HASH=your_api_hash
# ... add all other variables

# 6. Deploy with variables
railway up
Deploy on Koyeb
Push code to GitHub

Go to Koyeb

Click "Create App"

Select GitHub repository

Choose "Docker" as deployment method

Add environment variables

Deploy

Deploy on Heroku (Alternative)
bash
# 1. Install Heroku CLI
curl https://cli-assets.heroku.com/install.sh | sh

# 2. Login
heroku login

# 3. Create app
heroku create your-bot-name

# 4. Add buildpacks
heroku buildpacks:add heroku/python
heroku buildpacks:add https://github.com/jonathanong/heroku-buildpack-ffmpeg-latest.git

# 5. Add MongoDB addon
heroku addons:create mongodb:sandbox

# 6. Add Redis addon
heroku addons:create rediscloud:30

# 7. Set environment variables
heroku config:set API_ID=your_api_id
heroku config:set API_HASH=your_api_hash
# ... set all other variables

# 8. Deploy
git push heroku main

# 9. Start worker
heroku ps:scale worker=1
🔧 Troubleshooting
Common Issues and Solutions
Bot Doesn't Join Voice Chat
Problem: Bot fails to join voice chat or leaves immediately.

Solutions:

Ensure bot has admin permissions in the group

Check if voice chat is active

Verify the bot has Manage Voice Chats permission

Check if silence.mp3 exists in the root directory

bash
# Generate silence.mp3 if missing
ffmpeg -f lavfi -i anullsrc=r=44100:cl=mono -t 1 -q:a 9 -acodec libmp3lame silence.mp3
No Audio Playing
Problem: Bot joins voice chat but no audio plays.

Solutions:

Check FFmpeg installation:

bash
ffmpeg -version
Verify network connectivity to YouTube/Spotify

Check download directory permissions:

bash
chmod 755 downloads
Check logs for specific errors:

bash
tail -f logs/bot_*.log
MongoDB Connection Error
Problem: pymongo.errors.ServerSelectionTimeoutError

Solutions:

Ensure MongoDB is running:

bash
sudo systemctl status mongod
sudo systemctl start mongod
Check MongoDB URI in .env:

env
MONGO_URI=mongodb://localhost:27017
If using MongoDB Atlas, ensure IP whitelist includes your server

Redis Connection Error
Problem: redis.exceptions.ConnectionError

Solutions:

Ensure Redis is running:

bash
sudo systemctl status redis-server
sudo systemctl start redis-server
Test Redis connection:

bash
redis-cli ping
# Should return: PONG
YouTube Download Errors
Problem: yt-dlp fails to download videos.

Solutions:

Update yt-dlp:

bash
pip install --upgrade yt-dlp
Clear cache:

bash
rm -rf downloads/*
Use cookies file for age-restricted content:

Export cookies from browser

Save as cookies.txt in bot directory

High Memory Usage
Problem: Bot consumes too much RAM.

Solutions:

Reduce cache size in configuration

Set up cron job to clear old downloads:

bash
# Add to crontab
0 * * * * find /path/to/downloads -type f -mtime +1 -delete
Limit concurrent downloads in downloader.py

Use Redis for session management instead of memory

Rate Limiting Issues
Problem: Bot gets rate limited by Telegram.

Solutions:

Implement delays between messages

Use flood wait handling:

python
try:
    await message.reply("Response")
except FloodWait as e:
    await asyncio.sleep(e.value)
Reduce number of simultaneous operations

Logging and Debugging
Enable Debug Logging
env
# In .env file
LOG_LEVEL=DEBUG
View Logs
bash
# Systemd service logs
sudo journalctl -u telegram-music-bot -f

# Docker logs
docker-compose logs -f bot

# File logs
tail -f logs/bot_$(date +%Y%m%d).log
Debug Mode
Run bot with debug flag:

bash
python -m bot.main --debug
❓ FAQ
General Questions
Q: Can I use this bot in multiple groups?
A: Yes! The bot supports unlimited groups simultaneously. Each group has its own queue and settings.

Q: Does the bot support 24/7 playback?
A: Yes, the bot can stay in voice chat indefinitely. Enable AUTO_REJOIN=true for automatic recovery.

Q: How many songs can be in the queue?
A: Configurable via MAX_QUEUE_SIZE (default: 50). Can be increased based on server resources.

Q: Does the bot support playlists?
A: Yes, supports YouTube playlists and Spotify playlists/albums.

Technical Questions
Q: What's the minimum VPS requirement?
A: 1 CPU, 1GB RAM, 20GB SSD. Recommended: 2 CPU, 2GB RAM for optimal performance.

Q: How do I backup my data?
A:

bash
# MongoDB backup
mongodump --db telegram_music_bot --out /backup/

# Redis backup
redis-cli SAVE
cp /var/lib/redis/dump.rdb /backup/
Q: Can I use SQLite instead of MongoDB?
A: Yes, but you'll need to modify database/mongo.py to use SQLite. MongoDB is recommended for scalability.

Q: How do I update the bot?

bash
git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart telegram-music-bot
Usage Questions
Q: How do I make the bot admin-only?
A: Use the /settings command to restrict commands to admins only.

Q: Can I change the command prefix?
A: Edit handlers/commands.py and change the filters (e.g., filters.command("play", prefixes=["!", "."])).

Q: How do I add custom audio filters?
A: Add new filters in player/filters.py using FFmpeg filter syntax.

🤝 Contributing
We welcome contributions! Please follow these steps:

Development Setup
Fork the repository

Clone your fork:

bash
git clone https://github.com/yourusername/telegram-vc-music-bot.git
Create a new branch:

bash
git checkout -b feature/amazing-feature
Make your changes

Test thoroughly

Commit with clear message:

bash
git commit -m "Add amazing feature"
Push to your fork:

bash
git push origin feature/amazing-feature
Create a Pull Request

Code Style
Follow PEP 8 guidelines

Use type hints

Write docstrings for all functions

Keep functions small and focused

Use async/await properly

Testing
bash
# Run tests
python -m pytest tests/

# Run linter
flake8 bot/

# Type checking
mypy bot/
📄 License
This project is licensed under the MIT License - see below for details:

text
MIT License

Copyright (c) 2024 Your Name

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
🙏 Acknowledgments
Libraries Used
Pyrogram - Telegram MTProto API Framework

Py-TgCalls - Voice Chat Library

yt-dlp - YouTube Downloader

Motor - Async MongoDB Driver

redis-py - Redis Client

aiohttp - Async HTTP Client

Pillow - Image Processing

Inspiration
CallsMusic

tgmusicbot

MusicPlayer

📞 Support
Get Help
Documentation: Wiki

Issues: GitHub Issues

Discussions: GitHub Discussions

Telegram Channel: @yourchannel

Telegram Group: @yourgroup

Report Bugs
When reporting bugs, please include:

Bot version

Python version

Operating system

Error logs

Steps to reproduce

Feature Requests
We love new ideas! Please check existing requests first, then create a new issue with the "enhancement" label.

📊 Stats
https://img.shields.io/github/stars/yourusername/telegram-vc-music-bot?style=social
https://img.shields.io/github/forks/yourusername/telegram-vc-music-bot?style=social
https://img.shields.io/github/issues/yourusername/telegram-vc-music-bot
https://img.shields.io/github/issues-pr/yourusername/telegram-vc-music-bot
https://img.shields.io/github/last-commit/yourusername/telegram-vc-music-bot

<div align="center">
Made with ❤️ for the Telegram community

If this project helped you, please consider giving it a ⭐

</div> ```
This is the complete README.md file. You can copy this entire block and save it as README.md in your project root directory. The file includes:

Complete feature list

Detailed installation instructions for all platforms

Configuration guide with all environment variables

All commands with examples

Architecture overview

Deployment guides for VPS, Docker, and cloud platforms

Comprehensive troubleshooting section

FAQ

Contributing guidelines

License information

Support channels

The README is designed to be beginner-friendly while containing all the technical details needed for advanced users and production deployment.

