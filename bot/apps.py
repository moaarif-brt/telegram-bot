from django.apps import AppConfig
from django.core.management import call_command


class BotConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bot'
    # def ready(self):
    #     # Automatically start the bot when Django starts
    #     call_command('run_telegram_bot')