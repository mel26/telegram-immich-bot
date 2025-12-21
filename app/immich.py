import logging
import requests
import config
import utils
import os

from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes, CommandHandler

logger = logging.getLogger(__name__)

async def get_immich_status():
    """Check Immich server status and user info."""
    immich_status = "❌ Disconnected"
    user_info = "Unknown user"

    try:
        ping_response = requests.get(
            f"{config.IMMICH_API_URL}/server/ping",
            headers={'x-api-key': config.IMMICH_API_KEY},
            timeout=5
        )

        if ping_response.status_code == 200:
            immich_status = f"✅ Connected to Immich ({config.IMMICH_API_URL})"

            # If reachable, get user info
            try:
                user_response = requests.get(
                    f"{config.IMMICH_API_URL}/users/me",
                    headers={'x-api-key': config.IMMICH_API_KEY},
                    timeout=5
                )
                if user_response.status_code == 200:
                    user_data = user_response.json()
                    user_info = f"👤 {user_data.get('name', 'Unknown')}"
                    if user_data.get('isAdmin', False):
                        user_info += " [Admin]"
            except Exception as e:
                logger.error(f"Failed to get user info: {e}")
                user_info = "⚠️ Could not retrieve user info"
        else:
            immich_status = f"❌ Server ping failed (HTTP {ping_response.status_code})"

    except Exception as e:
        logger.error(f"Failed to connect to Immich: {e}")
        immich_status = f"❌ Connection failed: {str(e)}"

    return immich_status, user_info

async def upload_to_immich(filename: str, update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    # Metadata
    file_created_at, file_modified_at = utils.get_image_metadata(filename)
    logger.info(file_created_at)
    logger.info(file_modified_at)

    device_asset_id = os.path.basename(filename)
    checksum = utils.calculate_sha1(filename)

    with open(filename, 'rb') as f:
        files = {'assetData': (device_asset_id, f)}

        data = {
            'deviceAssetId': device_asset_id,
            'deviceId': 'telegram-bot-device',
            'fileCreatedAt': file_created_at,
            'fileModifiedAt': file_modified_at,
            'isFavorite': 'false',
            'visibility': 'timeline'
        }

        headers = {
            'x-api-key': config.IMMICH_API_KEY,
            'x-immich-checksum': checksum
        }

        logger.info(f"Uploading photo {device_asset_id} to Immich")
        response = requests.post(
            f"{config.IMMICH_API_URL}/assets",
            headers=headers,
            files=files,
            data=data
        )

        if not response.status_code in (200, 201):
            logger.error(f"Failed to upload asset {device_asset_id} to Immich. Status code: {response.status_code}, Response: {response.text}")
            await update.message.reply_text(f"❌ Failed to upload asset. Error: {response.text}")
            return

        response_data = response.json()
        if response.status_code == 200 and response_data.get('status') == 'duplicate':
            logger.info(f"Asset {device_asset_id} is a duplicate in Immich")
            await update.message.reply_text(f"ℹ️ Asset already exists in Immich.")
            return


        # update asset to set timezone
        data = {
            'dateTimeOriginal': file_created_at,
        }

        response = requests.put(
            f"{config.IMMICH_API_URL}/assets/" + response_data.get('id'),
            headers=headers,
            data=data
        )
        
        logger.info(f"Successfully uploaded asset {device_asset_id} to Immich")
        await update.message.reply_text(f"✅ Asset uploaded successfully!")
            
