from aiogram import Bot, Dispatcher, types, executor
import logging

from sqlalchemy import select, insert, delete, desc, update
from db.accessor import session_maker, engine
from db.models import *

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)
# Объект бота
# bot = Bot(token="5847893374:AAE6__0Eja6PHQk5gzFdj_k7bMSPL5fYPFE")  # тестовый
bot = Bot(token="6933554921:AAF0jje-04JjJLR5mj_2CTDxm5fFfb6bEB4")  # рабочий
# Диспетчер
dp = Dispatcher(bot)
