# 🎵 Telegram Voice Chat VC Music Bot

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

Docker Deployment
bash
# Using docker-compose
docker-compose up -d

# Or build manually
docker build -t music-bot .
docker run -d --env-file .env music-bot
⚙️ Configuration
Edit the .env file with your credentials:

env
API_ID=your_api_id
API_HASH=your_api_hash
BOT_TOKEN=your_bot_token
MONGO_URI=mongodb://localhost:27017
REDIS_URL=redis://localhost:6379/0
OWNER_ID=your_telegram_id
📚 Commands
Command	Description
/play <query>	Play or queue a song
/pause	Pause playback
/resume	Resume playback
/skip	Skip to next song
/stop	Stop and clear queue
/queue	Show current queue
/shuffle	Shuffle queue
/loop	Toggle loop mode
/volume <0-200>	Adjust volume
/lyrics	Get lyrics for current song
/settings	Bot settings (admin)
🏗️ Architecture
text
bot/
├── main.py           # Entry point
├── config.py         # Configuration
├── database/         # MongoDB & Redis
├── handlers/         # Command & callback handlers
├── player/           # Core player logic
├── services/         # External services (YouTube, Spotify)
├── ui/              # Keyboards & messages
└── utils/           # Helper functions
🔧 Troubleshooting
Bot doesn't join voice chat:

Ensure bot has admin permissions

Check if voice chat is active

Verify FFmpeg installation

No audio playing:

Check logs for download errors

Verify network connectivity

Ensure sufficient disk space

High CPU usage:

Increase cache size

Limit concurrent downloads

Use Redis for session management

📖 Documentation
For detailed documentation, visit our Wiki.

🤝 Contributing
Contributions are welcome! Please read our Contributing Guide.

📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

🙏 Acknowledgments
Pyrogram

Py-TgCalls

yt-dlp

📞 Support
Telegram Channel: @yourchannel

Issues: GitHub Issues

text

### 📄 **deploy.sh**
```bash
#!/bin/bash

# Telegram Voice Chat Music Bot Deployment Script
# For Ubuntu/Debian systems

set -e

echo "🎵 Telegram VC Music Bot Deployment Script"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
    echo -e "${YELLOW}⚠️  Running as root, creating a dedicated user is recommended${NC}"
fi

# Update system
echo -e "${GREEN}📦 Updating system packages...${NC}"
sudo apt update && sudo apt upgrade -y

# Install dependencies
echo -e "${GREEN}📦 Installing system dependencies...${NC}"
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    ffmpeg \
    redis-server \
    git \
    curl \
    wget

# Install MongoDB
echo -e "${GREEN}📦 Installing MongoDB...${NC}"
if ! command -v mongod &> /dev/null; then
    curl -fsSL https://www.mongodb.org/static/pgp/server-7.0.asc | sudo gpg --dearmor -o /usr/share/keyrings/mongodb-server-7.0.gpg
    echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list
    sudo apt update
    sudo apt install -y mongodb-org
    sudo systemctl start mongod
    sudo systemctl enable mongod
fi

# Start Redis
echo -e "${GREEN}📦 Starting Redis...${NC}"
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Create bot directory
echo -e "${GREEN}📁 Creating bot directory...${NC}"
BOT_DIR="/opt/telegram-music-bot"
sudo mkdir -p $BOT_DIR
sudo chown $USER:$USER $BOT_DIR
cd $BOT_DIR

# Clone repository (replace with your repo)
echo -e "${GREEN}📥 Cloning repository...${NC}"
if [ ! -d ".git" ]; then
    git clone https://github.com/yourusername/telegram-vc-music-bot.git .
else
    git pull
fi

# Setup Python environment
echo -e "${GREEN}🐍 Setting up Python environment...${NC}"
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
echo -e "${GREEN}📁 Creating directories...${NC}"
mkdir -p downloads logs cache

# Setup environment file
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  Creating .env file, please edit with your credentials${NC}"
    cp .env.example .env
    echo -e "${RED}❗ Please edit $BOT_DIR/.env with your Telegram credentials!${NC}"
fi

# Create systemd service
echo -e "${GREEN}🔧 Creating systemd service...${NC}"
sudo tee /etc/systemd/system/telegram-music-bot.service > /dev/null <<EOF
[Unit]
Description=Telegram VC Music Bot
After=network.target mongod.service redis-server.service
Wants=mongod.service redis-server.service

[Service]
Type=simple
User=$USER
WorkingDirectory=$BOT_DIR
Environment="PATH=$BOT_DIR/venv/bin"
ExecStart=$BOT_DIR/venv/bin/python -m bot.main
Restart=on-failure
RestartSec=10
StandardOutput=append:$BOT_DIR/logs/bot.log
StandardError=append:$BOT_DIR/logs/error.log

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and start service
echo -e "${GREEN}🚀 Starting bot service...${NC}"
sudo systemctl daemon-reload
sudo systemctl enable telegram-music-bot
sudo systemctl start telegram-music-bot

# Check status
echo -e "${GREEN}✅ Deployment complete!${NC}"
echo ""
echo "📊 Service Status:"
sudo systemctl status telegram-music-bot --no-pager

echo ""
echo -e "${YELLOW}📝 Next steps:${NC}"
echo "1. Edit $BOT_DIR/.env with your credentials"
echo "2. Restart the bot: sudo systemctl restart telegram-music-bot"
echo "3. Check logs: sudo journalctl -u telegram-music-bot -f"
echo ""
echo -e "${GREEN}🎉 Bot should now be running!${NC}"
📄 requirements.txt
txt
# Core dependencies
pyrogram>=2.3.0
py-tgcalls>=2.0.1
yt-dlp>=2024.12.0

# Databases
motor>=3.4.0
redis>=5.0.0

# Async HTTP
aiohttp>=3.9.0
aiofiles>=23.2.0

# Image processing
Pillow>=10.0.0

# Configuration
python-dotenv>=1.0.0
pydantic>=2.5.0
pydantic-settings>=2.1.0

# Spotify integration
spotipy>=2.24.0

# Utilities
beautifulsoup4>=4.12.0
langcodes>=3.4.0
psutil>=5.9.0
uvloop>=0.19.0

# Web dashboard (optional)
fastapi>=0.104.0
uvicorn>=0.24.0
jinja2>=3.1.0
This is the complete repository structure with all files needed for your Telegram Voice Chat Music Bot. To use this:

Create a new directory called telegram_vc_music_bot

Create all the subdirectories as shown in the tree structure

Copy each code block into its respective file

Create the .env file from the example

Generate or download the silence.mp3 file

Install dependencies with pip install -r requirements.txt

Run the bot with python -m bot.main

The bot is fully modular, production-ready, and includes all requested features including YouTube/Spotify support, queue management, lyrics, thumbnails, Docker deployment, and more.


