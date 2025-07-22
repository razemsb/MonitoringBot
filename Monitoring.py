import os
import discord
from discord.ext import commands
from telegram import Bot
from dotenv import load_dotenv
import asyncio
import threading
import logging

# Загрузка переменных окружения
load_dotenv()

# Настройка логгирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Конфигурация бота
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Инициализация Discord бота
intents = discord.Intents.default()
intents.voice_states = True  # Для отслеживания голосовых каналов
discord_bot = commands.Bot(command_prefix="!", intents=intents)

# Инициализация Telegram бота
telegram_bot = Bot(token=TELEGRAM_TOKEN)

@discord_bot.event
async def on_ready():
    logger.info(f"Discord Bot готов! Имя: {discord_bot.user.name}")

@discord_bot.event
async def on_voice_state_update(member, before, after):
    # Если пользователь зашёл в голосовой канал
    if before.channel != after.channel and after.channel is not None:
        message = f"🎤 {member.name} зашёл в канал: {after.channel.name}"
        logger.info(message)
        await send_telegram_message(message)

    # Если пользователь вышел из голосового канала (опционально)
    elif before.channel != after.channel and before.channel is not None:
        message = f"🚪 {member.name} вышел из канала: {before.channel.name}"
        logger.info(message)
        await send_telegram_message(message)

async def send_telegram_message(text):
    try:
        await telegram_bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=text)
    except Exception as e:
        logger.error(f"Ошибка отправки в Telegram: {e}")

def start_discord_bot():
    discord_bot.run(DISCORD_TOKEN)

def console_control():
    while True:
        cmd = input("Введите команду (stop/exit для выхода): ").strip().lower()
        if cmd in ("stop", "exit"):
            logger.info("Остановка бота...")
            loop = asyncio.get_event_loop()
            loop.create_task(discord_bot.close())
            break

if __name__ == "__main__":
    # Запуск Discord бота в отдельном потоке
    discord_thread = threading.Thread(target=start_discord_bot)
    discord_thread.start()

    # Запуск консольного управления
    console_control()