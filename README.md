# YouTube to MP3 Telegram Bot

A Telegram bot that converts YouTube videos to high-quality MP3 files. Built with Python and yt-dlp.

## Features

- Convert YouTube videos to MP3 format
- High-quality audio extraction
- Automatic file size checking
- Optimized for slow connections
- Background service support
- Detailed logging

## Prerequisites

- Python 3.11 or higher
- FFmpeg
- Telegram Bot Token (get it from [@BotFather](https://t.me/botfather))

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/youtube-agent.git
cd youtube-agent
```

2. Create and activate virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file:
```bash
echo "TELEGRAM_TOKEN=your_bot_token_here" > .env
```

## Running the Bot

### Development
```bash
python3 youtube_telegram_bot.py
```

### Production (Ubuntu)
1. Create systemd service:
```bash
sudo cp youtube-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl start youtube-bot
sudo systemctl enable youtube-bot
```

2. Monitor logs:
```bash
sudo journalctl -u youtube-bot -f
```

## Usage

1. Start the bot with `/start` command
2. Send a YouTube video URL
3. Wait for the bot to process and send the MP3 file

## Configuration

The bot can be configured through environment variables:
- `TELEGRAM_TOKEN`: Your Telegram bot token
- `DOWNLOAD_DIR`: Directory for temporary files (default: 'downloads')

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) for YouTube video downloading
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) for the Telegram API wrapper 