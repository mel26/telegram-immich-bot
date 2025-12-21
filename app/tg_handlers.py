import logging
import config
import utils
import os
import immich

from enum import Enum, auto

from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes, CommandHandler

class TG_MediaType(Enum):
    MEDIA_PHOTO =    1
    MEDIA_VIDEO =    2
    MEDIA_DOC   =    3

logger = logging.getLogger(__name__)

# -------------------------------------------------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Alias for help command."""
    await help_command(update, context)

# -------------------------------------------------------------------------
async def send_startup_message(application: Application):
    """Send startup message to all allowed users when container starts."""
    immich_status, user_info = await immich.get_immich_status()

    startup_message = (
        f"🤖 {config.BOT_NAME} v{config.BOT_VERSION} has started!\n\n"
        f"{immich_status}\n"
        f"Logged in as {user_info}\n\n"
        "Bot is ready to receive your files."
    )

    logger.info(f"Sending startup messages to {len(config.ALLOWED_USER_IDS)} allowed users")

    for user_id in config.ALLOWED_USER_IDS:
        try:
            await application.bot.send_message(
                chat_id=user_id,
                text=startup_message
            )
            logger.info(f"Successfully sent startup message to user {user_id}")
        except Exception as e:
            logger.error(f"Failed to send startup message to user {user_id}: {e}")

# -------------------------------------------------------------------------
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a help message with Immich connection status."""
    immich_status, user_info = await get_immich_status()

    help_message = (
        f"ℹ️ {config.BOT_NAME} v{config.BOT_VERSION}\n\n"
        f"{immich_status}\n"
        f"Logged in as {user_info}\n\n"
        "Available commands:\n"
        "/help - Show this help message\n"
        "/version - Show bot version\n"
        "/files - Show supported file types\n\n"
        "Send me files and I'll upload them to your Immich instance!"
    )

    await update.message.reply_text(help_message)

# -------------------------------------------------------------------------
async def version(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send the bot version when the command /version is issued."""
    await update.message.reply_text(f"📋 {config.BOT_NAME} version: {config.BOT_VERSION}")

# -------------------------------------------------------------------------
async def files(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send supported file types when the command /files is issued."""
    await update.message.reply_text(f"📄 Supported file types:\n{config.SUPPORTED_FILE_TYPES}")

# -------------------------------------------------------------------------
async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await handle_tg_media(update, context, TG_MediaType.MEDIA_DOC)
    return 

# -------------------------------------------------------------------------
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await handle_tg_media(update, context, TG_MediaType.MEDIA_PHOTO)
    return 

# -------------------------------------------------------------------------
async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await handle_tg_media(update, context, TG_MediaType.MEDIA_VIDEO)
    return 

async def handle_tg_media(update: Update, context: ContextTypes.DEFAULT_TYPE, mediaType: TG_MediaType):
    user_id = update.message.from_user.id
    username = update.message.from_user.username or update.message.from_user.first_name

    # Check user permission
    if not utils.is_user_allowed(user_id):
        logger.warning(f"Unauthorized upload attempt by user {username} (ID: {user_id})")
        await update.message.reply_text("❌ You are not authorized to use this bot.")
        return

    match mediaType:
        case TG_MediaType.MEDIA_PHOTO: 
            tg_asset = update.message.photo[-1]
            mimeType = "image/jpg"
        case TG_MediaType.MEDIA_VIDEO:
            tg_asset = update.message.video
            mimeType = "video/mp4"
        case TG_MediaType.MEDIA_DOC:
            tg_asset = update.message.document
            mimeType = tg_asset.mime_type
            if not mimeType.startswith("image/") | mimeType.startswith("video/") :
                await update.message.reply_text("❌ You've sent not a video or photo")
                return
        case _:
            await update.message.reply_text("❌ Some undefined media type is defined in the bot internally. Shit happened")
            return

    file_id = tg_asset.file_id
    logger.info(f"Processing asset upload from user {username} (ID: {user_id})")

    temp_file_path = ''
    file_name = ''
    try:
        file = await context.bot.get_file(file_id)

        if mimeType.startswith("image/"):
            file_name = f"photo_{file_id}.jpg"
        elif mimeType.startswith("video/"):
            file_name = f"video_{file_id}.mp4"
        else:
            ext = os.path.splitext(tg_asset.file_name)[-1]
            file_name = f"video_{file_id}{ext}"

        temp_file_path = f"/tmp/{file_name}"
        logger.info(f"Downloading asset {file_name} from Telegram to {temp_file_path}")
        await file.download_to_drive(temp_file_path)

        if not os.path.exists(temp_file_path):
            logger.error(f"Failed to download file {file_name}")
            await update.message.reply_text("❌ Failed to download file.")
            return

        await immich.upload_to_immich(temp_file_path, update, context)

    except Exception as e:
        logger.error(f"Error processing file {file_name}: {str(e)}", exc_info=True)
        await update.message.reply_text(f"❌ An error occurred: {str(e)}")

    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
            logger.info(f"Cleaned up temporary file: {temp_file_path}")
        else:
            logger.info(f"Temporary file: {temp_file_path} is not exists")