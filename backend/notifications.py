"""
Notification module for sending alerts to users

Currently supports Telegram Bot API
"""

import os
import requests
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram_notification(message: str) -> bool:
    """
    Send notification via Telegram

    Args:
        message: Message to send

    Returns:
        True if successful, False otherwise
    """
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram credentials not configured. Skipping notification.")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"Failed to send Telegram notification: {e}")
        return False

def notify_status_change(tracking_number: str, carrier: str, old_status: str, new_status: str, alias: Optional[str] = None):
    """
    Send notification when package status changes

    Args:
        tracking_number: Tracking number
        carrier: Carrier code
        old_status: Previous status
        new_status: New status
        alias: User-friendly package name (optional)
    """
    package_name = alias or tracking_number

    message = f"""
<b>📦 Package Status Update</b>

<b>Package:</b> {package_name}
<b>Tracking:</b> {tracking_number}
<b>Carrier:</b> {carrier}

<b>Status Changed:</b>
{old_status} → {new_status}
"""

    send_telegram_notification(message.strip())

def notify_delivery_complete(tracking_number: str, carrier: str, alias: Optional[str] = None):
    """
    Send notification when package is delivered

    Args:
        tracking_number: Tracking number
        carrier: Carrier code
        alias: User-friendly package name (optional)
    """
    package_name = alias or tracking_number

    message = f"""
<b>✅ Package Delivered!</b>

<b>Package:</b> {package_name}
<b>Tracking:</b> {tracking_number}
<b>Carrier:</b> {carrier}

Your package has been delivered!
"""

    send_telegram_notification(message.strip())

def notify_error(tracking_number: str, carrier: str, error: str, alias: Optional[str] = None):
    """
    Send notification when tracking error occurs

    Args:
        tracking_number: Tracking number
        carrier: Carrier code
        error: Error message
        alias: User-friendly package name (optional)
    """
    package_name = alias or tracking_number

    message = f"""
<b>⚠️ Tracking Error</b>

<b>Package:</b> {package_name}
<b>Tracking:</b> {tracking_number}
<b>Carrier:</b> {carrier}

<b>Error:</b> {error}
"""

    send_telegram_notification(message.strip())
