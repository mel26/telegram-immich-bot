import os
import logging
from zoneinfo import ZoneInfo

IMMICH_API_URL = os.getenv("IMMICH_API_URL")
IMMICH_API_KEY = os.getenv("IMMICH_API_KEY")
IMMICH_SELECTED_ALBUM = os.getenv("IMMICH_SELECTED_ALBUM")
IMMICH_SELECTED_ALBUM_NAME = ""

UPLOAD_TIMEZONE = ZoneInfo(os.getenv("UPLOAD_TIMEZONE", "Europe/Moscow"))

BOT_NAME = "Telegram to Immich Bot"
BOT_VERSION = "0.7"
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

SUPPORTED_IMAGE_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.heic', '.heif', '.webp')
SUPPORTED_VIDEO_EXTENSIONS = ('.mp4', '.avi', '.mov', '.webm', '.mpg', '.mpeg')
SUPPORTED_EXTENSIONS = SUPPORTED_IMAGE_EXTENSIONS + SUPPORTED_VIDEO_EXTENSIONS
SUPPORTED_FILE_TYPES = (
    "Images: JPG, PNG, GIF, BMP, TIFF, HEIC, WEBP\n"
    "Videos: MP4, AVI, MOV, WEBM, MPEG"
)

allowed_user_ids = os.getenv("ALLOWED_USER_IDS")
if not allowed_user_ids:
    raise ValueError("ALLOWED_USER_IDS environment variable is required")

ALLOWED_USER_IDS = [int(user_id.strip()) for user_id in allowed_user_ids.split(",") if user_id.strip()]

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)

def validate_config():
    """Validate required environment variables."""
    missing_vars = []

    if not TELEGRAM_BOT_TOKEN:
        missing_vars.append("TELEGRAM_BOT_TOKEN")
    if not IMMICH_API_KEY:
        missing_vars.append("IMMICH_API_KEY")
    if not IMMICH_API_URL:
        missing_vars.append("IMMICH_API_URL")
    if not ALLOWED_USER_IDS:
        missing_vars.append("ALLOWED_USER_IDS")
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")