import time
import logging
import requests
import threading
import telebot
from algo import run_analysis
from dotenv import load_dotenv
import os

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
BOT_OWNER_ID = os.getenv('BOT_OWNER_ID')  # Add this to your .env file

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
analyzer_running = False
analyzer_thread = None

def send_telegram_notification(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"  # Or "HTML" if you prefer
    }
    try:
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            logging.info("Telegram notification sent successfully.")
        else:
            logging.error(f"Failed to send telegram notification: {response.text}")
    except Exception as e:
        logging.error(f"Exception in sending telegram notification: {e}")

def analyze_signals():
    global analyzer_running
    while analyzer_running:
        logging.info("Running Signal Analysis...")
        signals = run_analysis()
        if signals:
            for msg in signals:
                send_telegram_notification(msg)
        else:
            logging.info("No signals detected.")
        time.sleep(300)  # Adjust timing as needed

def is_owner(message):
    return str(message.from_user.id) == BOT_OWNER_ID

@bot.message_handler(commands=["start"])
def start_analyzer(message):
    global analyzer_running, analyzer_thread

    if not is_owner(message):
        bot.reply_to(message, "You are not authorized to use this command.")
        logging.warning(f"Unauthorized access attempt by user {message.from_user.id}")
        return

    if analyzer_running:
        bot.reply_to(message, "Analyzer is already running!")
        logging.info("Analyzer is already running!")
    else:
        analyzer_running = True
        analyzer_thread = threading.Thread(target=analyze_signals, daemon=True)
        analyzer_thread.start()
        bot.reply_to(message, "Analyzer started!")
        logging.info("Analyzer started!")

@bot.message_handler(commands=["stop"])
def stop_analyzer(message):
    global analyzer_running

    if not is_owner(message):
        bot.reply_to(message, "You are not authorized to use this command.")
        logging.warning(f"Unauthorized access attempt by user {message.from_user.id}")
        return

    if not analyzer_running:
        bot.reply_to(message, "Analyzer is already stopped!")
        logging.info("Analyzer is already stopped!")
    else:
        analyzer_running = False
        bot.reply_to(message, "Analyzer stopped!")
        logging.info("Analyzer stopped!")
