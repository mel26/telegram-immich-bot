import logging
import os
import mimetypes
import config
import hashlib
from datetime import datetime, timezone

from PIL import Image
from PIL.ExifTags import TAGS

logger = logging.getLogger(__name__)

def get_file_type(file_path):
    """Determine file type based on extension and MIME type."""
    ext = os.path.splitext(file_path)[1].lower()
    mime_type, _ = mimetypes.guess_type(file_path)

    if ext in config.SUPPORTED_IMAGE_EXTENSIONS:
        return "image"
    elif ext in config.SUPPORTED_VIDEO_EXTENSIONS:
        return "video"
    elif mime_type and mime_type.startswith('video/'):
        return "video"
    elif mime_type and mime_type.startswith('image/'):
        return "image"
    return "other"

def format_iso_date_with_timezone(dt):
    """Format datetime as ISO 8601 with configured timezone."""
    dt = dt.astimezone(config.UPLOAD_TIMEZONE)
    s = dt.isoformat().split("+")
    return s[0][:-3] + "+" + s[1]

def calculate_sha1(file_path):
    """Calculate SHA1 checksum of a file."""
    sha1 = hashlib.sha1()
    with open(file_path, 'rb') as f:
        while True:
            data = f.read(65536)
            if not data:
                break
            sha1.update(data)
    return sha1.hexdigest()

def get_image_metadata(file_path):
    """Extract metadata from image files."""
    try:
        with Image.open(file_path) as img:
            exif_data = img._getexif() or {}
            metadata = {TAGS.get(tag, tag): value for tag, value in exif_data.items()}

            if 'DateTimeOriginal' in metadata:
                created_at = datetime.strptime(metadata['DateTimeOriginal'], '%Y:%m:%d %H:%M:%S')
                created_at = created_at.replace(tzinfo=config.UPLOAD_TIMEZONE)
            elif 'DateTime' in metadata:
                created_at = datetime.strptime(metadata['DateTime'], '%Y:%m:%d %H:%M:%S')
                created_at = created_at.replace(tzinfo=config.UPLOAD_TIMEZONE)
            else:
                created_at = datetime.fromtimestamp(os.path.getmtime(file_path), timezone.utc)

            return format_iso_date_with_timezone(created_at), format_iso_date_with_timezone(created_at)
    except Exception:
        now = datetime.now(timezone.utc)
        return format_iso_date_with_timezone(now), format_iso_date_with_timezone(now)
    
def is_user_allowed(user_id):
    """Check if a user is allowed to upload files. If not set, all users can upload files"""
    if not config.ALLOWED_USER_IDS:
        return True
    return user_id in config.ALLOWED_USER_IDS