"""Настройки бота"""
import os
from dotenv import load_dotenv

from aiogram import Dispatcher, Bot
from aiogram.contrib.fsm_storage.memory import MemoryStorage

load_dotenv()
# Бот
bot = Bot(os.getenv("BOT_TOKEN"))
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# База данных
DB_NAME = "database.sqlite"

ADMINS = {
    "Alisher": 788348199
}   `
