import asyncio

import json
import time

import emoji
import requests
from aiogram import executor
from aiogram.utils.markdown import hlink
from aiohttp import ClientSession

from bot.additional_funks import *
from bot.bot_creating import *
from bot.bot_commands import *
from config import ID_G, TOKEN
# отправка создателю сообщения о запуске бота
# url = f'https://api.telegram.org/bot5603755641:AAF5EXjubgZDFdaX-cbKqfqPXjqYuVRpgeE/sendMessage'
# data = {'chat_id': ID_G, 'text': "Бот был запущен"}
# requests.post(url, data).json()

# Запуск процесса поллинга новых апдейтов
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_start)
