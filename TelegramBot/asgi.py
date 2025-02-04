"""
ASGI config for TelegramBot project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from telegram_bot import bot
import threading

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TelegramBot.settings')

application = get_asgi_application()

# Start the Telegram bot in a separate thread
def run_bot():
    bot.polling(none_stop=True)

bot_thread = threading.Thread(target=run_bot)
bot_thread.daemon = True  # This ensures the bot thread exits when the main thread exits
bot_thread.start()