from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes, CommandHandler
import logging
import asyncio

import tg_handlers
import config

logger = logging.getLogger(__name__)

def main():
    """Start the bot with command handlers."""
    try:
        config.validate_config()

        application = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()
                
        album_name = ""
        if config.IMMICH_SELECTED_ALBUM:
            try:
                import requests
                response = requests.get(
                    f"{config.IMMICH_API_URL}/albums/{config.IMMICH_SELECTED_ALBUM}?withoutAssets=true",
                    headers={'x-api-key': config.IMMICH_API_KEY},
                    timeout=5
                )
                if response.status_code == 200:
                    album_data = response.json()
                    album_name = album_data.get('albumName', 'Unknown Album')
                else:
                    logger.error(f"Failed to get album name (HTTP {response.status_code})")
                    return
            except Exception as e:
                logger.error(f"Failed to get album name: {e}")
                return
            config.IMMICH_SELECTED_ALBUM_NAME = album_name
                
        application.add_handler(CommandHandler("start",                 tg_handlers.start))
        application.add_handler(CommandHandler("help",                  tg_handlers.help_command))
        application.add_handler(CommandHandler("version",               tg_handlers.version))
        application.add_handler(CommandHandler("files",                 tg_handlers.files))
        application.add_handler(MessageHandler(filters.Document.ALL,    tg_handlers.handle_document))
        application.add_handler(MessageHandler(filters.PHOTO,           tg_handlers.handle_photo))
        application.add_handler(MessageHandler(filters.VIDEO,           tg_handlers.handle_video))

        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        if loop.is_running():
            asyncio.create_task(tg_handlers.send_startup_message(application))
        else:
            loop.run_until_complete(tg_handlers.send_startup_message(application))

        logger.info(f"{config.BOT_NAME} v{config.BOT_VERSION} started successfully")
        logger.info(f"Allowed users: {config.ALLOWED_USER_IDS}")

        application.run_polling(allowed_updates=Update.ALL_TYPES)

    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        raise

if __name__ == '__main__':
    main()
