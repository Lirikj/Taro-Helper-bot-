import os
import telebot


BOT_TOKEN = os.getenv('BOT_TOKEN')
API_KEY = os.getenv('API_KEY')
DEVELOPER_STR = os.getenv('DEVELOPER')


bot = telebot.TeleBot(BOT_TOKEN)
