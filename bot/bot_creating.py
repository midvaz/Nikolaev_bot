from aiogram import Bot, Dispatcher, types, executor
import logging
from config import TOKEN
from sqlalchemy import select, insert, delete, desc, update
from db.accessor import session_maker, engine
from db.models import *

# Включаем логирование, чтобы не пропустить важные сообщения
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)
logger.info("Starting bot")
# Объект бота
# bot = Bot(token="5847893374:AAE6__0Eja6PHQk5gzFdj_k7bMSPL5fYPFE")  # тестовый
bot = Bot(token= TOKEN)  # рабочий
# Диспетчер
dp = Dispatcher(bot)


