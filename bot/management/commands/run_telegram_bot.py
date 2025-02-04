from django.core.management.base import BaseCommand
import threading
from telegram_bot import bot  # Import your existing bot logic

# Function to run the bot
def run_bot():
    bot.polling()

class Command(BaseCommand):
    help = "Run the Telegram bot"

    def handle(self, *args, **kwargs):
        # Start the bot in a background thread
        threading.Thread(target=run_bot).start()
        self.stdout.write(self.style.SUCCESS('Telegram bot started successfully'))
