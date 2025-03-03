import os
import logging
import re
import socket
import requests
from pathlib import Path
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
import yt_dlp

# Configure logging with more detail
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configuration
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
DOWNLOAD_DIR = Path('downloads')
DOWNLOAD_DIR.mkdir(exist_ok=True)

def check_internet_connection():
    """Check if there's an active internet connection."""
    try:
        # Try to connect to Google's DNS server
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        logger.info("Internet connection is available")
        return True
    except OSError:
        logger.error("No internet connection available")
        return False

def check_telegram_api():
    """Check if Telegram API is accessible."""
    try:
        response = requests.get("https://api.telegram.org", timeout=5)
        if response.status_code == 200:
            logger.info("Telegram API is accessible")
            return True
        else:
            logger.error(f"Telegram API returned status code: {response.status_code}")
            return False
    except requests.RequestException as e:
        logger.error(f"Error checking Telegram API: {e}")
        return False

def is_valid_youtube_url(url: str) -> bool:
    """Validate if the URL is a valid YouTube URL."""
    youtube_regex = r'(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/)[a-zA-Z0-9_-]{11}'
    return bool(re.match(youtube_regex, url))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    logger.info(f"Start command received from user {update.effective_user.id}")
    await update.message.reply_text(
        'Hi! 👋\n\n'
        'Please send me a valid YouTube link and I will convert it to high-quality MP3 for you.\n\n'
        'Example: https://www.youtube.com/watch?v=...'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /help is issued."""
    logger.info(f"Help command received from user {update.effective_user.id}")
    await update.message.reply_text(
        'How to use this bot:\n\n'
        '1. Send me a YouTube video URL\n'
        '2. Wait while I download and convert it to MP3\n'
        '3. I will send you the high-quality MP3 file\n\n'
        'Note: Only valid YouTube URLs are accepted.'
    )

def download_youtube_audio(url: str) -> str:
    """Download YouTube video and convert to highest quality MP3."""
    logger.info(f"Starting download for URL: {url}")
    ydl_opts = {
        'format': 'm4a/bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '0',  # Highest quality
        }],
        'outtmpl': str(DOWNLOAD_DIR / '%(title)s.%(ext)s'),
        'quiet': True,
        # Cookie handling
        'cookiesfrombrowser': ('chrome',),  # Use Chrome cookies
        'cookiefile': 'cookies.txt',  # Fallback cookie file
        'cookiesfrombrowser': ('firefox',),  # Try Firefox cookies as backup
        # Mobile User-Agent and headers
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_2_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
            'Sec-Ch-Ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
            'Sec-Ch-Ua-Mobile': '?1',
            'Sec-Ch-Ua-Platform': '"iOS"',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'DNT': '1'
        },
        # Network optimizations
        'socket_timeout': 30,
        'retries': 10,
        'fragment_retries': 10,
        'extractor_retries': 10,
        'file_access_retries': 10,
        'concurrent_fragments': 10,
        'buffersize': 65536,
        'http_chunk_size': 20971520,
        # Zero delays for maximum speed
        'sleep_interval': 0,
        'max_sleep_interval': 0,
        'sleep_interval_requests': 0,
        'throttledratelimit': 1000000,
        'ratelimit': 1000000,
        'retry_sleep': 0,
        'fragment_retry_sleep': 0,
        'file_access_retry_sleep': 0,
        'extractor_retry_sleep': 0,
        # Downloader optimizations
        'downloader_args': {
            'http': ['--buffer-size=65536', '--max-connection-per-server=10']
        },
        'external_downloader_args': {
            'ffmpeg': ['-threads', '8']
        },
        'postprocessor_args': {
            'FFmpegExtractAudio': ['-threads', '8']
        },
        # YouTube specific optimizations
        'extractor_args': {
            'youtube': {
                'skip': ['dash', 'hls'],
                'player_skip': ['js', 'configs', 'webpage'],
                'player_client': ['android', 'ios'],  # Using mobile clients
                'player_params': {
                    'enablejsapi': '1',
                    'origin': 'https://www.youtube.com',
                    'widget_referrer': 'https://www.youtube.com'
                }
            }
        },
        # Additional security bypasses
        'no_check_certificates': True,
        'prefer_insecure': True,
        'legacyserverconnect': False,
        'no_warnings': True,
        'quiet': True,
        'no_color': True,
        'progress_hooks': [],
        'extract_flat': False,
        'force_generic_extractor': False,
        'geo_verification_proxy': '',
        'source_address': '0.0.0.0',
        # New anti-bot measures
        'compat_opts': ['no-youtube-channel-redirect', 'no-youtube-unavailable-videos']
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            logger.info("Attempting to download video...")
            info = ydl.extract_info(url, download=True)
            logger.info(f"Successfully downloaded: {info['title']}")
            return str(DOWNLOAD_DIR / f"{info['title']}.mp3")
    except Exception as e:
        logger.error(f"Error downloading video: {e}")
        raise

async def handle_youtube_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle YouTube URL and process it."""
    url = update.message.text.strip()
    user_id = update.effective_user.id
    logger.info(f"Received URL from user {user_id}: {url}")
    
    if not is_valid_youtube_url(url):
        logger.warning(f"Invalid YouTube URL received from user {user_id}")
        await update.message.reply_text(
            '❌ Please send a valid YouTube URL.\n\n'
            'Example: https://www.youtube.com/watch?v=...'
        )
        return
    
    try:
        # Send processing message
        processing_msg = await update.message.reply_text(
            '⏳ Processing your request...\n'
            'This may take a few minutes depending on the video length.'
        )
        
        # Download and convert to MP3
        mp3_path = download_youtube_audio(url)
        
        # Get file size
        file_size = os.path.getsize(mp3_path)
        logger.info(f"File size: {file_size / (1024*1024):.2f} MB")
        
        # Check if file is too large for Telegram (50MB limit)
        if file_size > 50 * 1024 * 1024:  # 50MB in bytes
            logger.warning(f"File too large for user {user_id}: {file_size / (1024*1024):.2f} MB")
            await processing_msg.edit_text(
                '❌ Sorry, this audio file is too large for Telegram (over 50MB).\n'
                'Please try a shorter video.'
            )
            os.remove(mp3_path)
            return
        
        # Upload to Telegram with increased timeout
        logger.info(f"Uploading file to user {user_id}")
        try:
            with open(mp3_path, 'rb') as audio_file:
                await context.bot.send_audio(
                    chat_id=update.effective_chat.id,
                    audio=audio_file,
                    caption=f"🎵 {Path(mp3_path).stem}",
                    title=Path(mp3_path).stem,
                    performer="YouTube Audio",
                    duration=0,  # Let Telegram determine duration
                    read_timeout=60,  # Increased timeout for reading
                    write_timeout=60,  # Increased timeout for writing
                    connect_timeout=60,  # Increased timeout for connection
                    pool_timeout=60  # Increased timeout for connection pool
                )
        except Exception as upload_error:
            logger.error(f"Upload error for user {user_id}: {upload_error}")
            # Try alternative upload method with longer timeouts
            try:
                with open(mp3_path, 'rb') as audio_file:
                    await context.bot.send_audio(
                        chat_id=update.effective_chat.id,
                        audio=audio_file,
                        caption=f"🎵 {Path(mp3_path).stem}",
                        title=Path(mp3_path).stem,
                        performer="YouTube Audio",
                        duration=0,
                        read_timeout=520,  # Even longer timeout
                        write_timeout=520,
                        connect_timeout=520,
                        pool_timeout=520
                    )
            except Exception as retry_error:
                logger.error(f"Retry upload failed for user {user_id}: {retry_error}")
                raise Exception("Failed to upload file after multiple attempts")
        
        # Clean up
        os.remove(mp3_path)
        logger.info(f"Successfully processed and sent file to user {user_id}")
        
        await processing_msg.edit_text('✅ Successfully processed and sent!')
        
    except Exception as e:
        logger.error(f"Error processing URL for user {user_id}: {e}")
        await update.message.reply_text(
            '❌ Sorry, there was an error processing your request.\n'
            'Please try again or check if the video is available.'
        )

def main():
    """Start the bot."""
    logger.info("Starting bot initialization...")
    
    if not TELEGRAM_TOKEN:
        logger.error("TELEGRAM_TOKEN not found in .env file")
        return
    
    logger.info(f"Bot token loaded: {TELEGRAM_TOKEN[:10]}...")
    
    # Check connectivity
    if not check_internet_connection():
        logger.error("Cannot start bot: No internet connection")
        return
    
    if not check_telegram_api():
        logger.error("Cannot start bot: Telegram API is not accessible")
        return
    
    try:
        # Create the Application and pass it your bot's token
        logger.info("Creating application...")
        application = Application.builder().token(TELEGRAM_TOKEN).build()

        # Add handlers
        logger.info("Adding command handlers...")
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_youtube_url))

        # Start the Bot
        logger.info("Starting bot polling...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except Exception as e:
        logger.error(f"Error starting bot: {e}")

if __name__ == '__main__':
    main() 