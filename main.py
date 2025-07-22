import os
import discord
from discord.ext import commands
from telegram import Bot
from dotenv import load_dotenv
import asyncio
import logging

load_dotenv()

# Конфигурация логгирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MyBot(commands.Bot):
    async def setup_hook(self):
        """Переопределение хука для корректного запуска"""
        await self.tree.sync()
        logger.info("Команды синхронизированы")

    async def close(self):
        """Правильное завершение работы"""
        await super().close()
        await self.http_session.close()

# Инициализация бота
intents = discord.Intents.default()
intents.voice_states = True
bot = MyBot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    logger.info(f"Бот готов: {bot.user.name}")

@bot.event
async def on_voice_state_update(member, before, after):
    if before.channel != after.channel:
        message = f"{member.name} {'зашел' if after.channel else 'вышел'} в {'канал '+after.channel.name if after.channel else 'из канала '+before.channel.name}"
        logger.info(message)
        await send_telegram_message(message)

async def send_telegram_message(text):
    try:
        telegram_bot = Bot(token=os.getenv("TELEGRAM_TOKEN"))
        await telegram_bot.send_message(
            chat_id=os.getenv("TELEGRAM_CHAT_ID"),
            text=text
        )
    except Exception as e:
        logger.error(f"Ошибка Telegram: {e}")

async def main():
    async with bot:
        await bot.start(os.getenv("DISCORD_TOKEN"))

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
