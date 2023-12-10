import asyncio
import datetime
import traceback

import emoji
import requests
from aiogram import types
from sqlalchemy import select

from bot.bot_creating import bot
from db.accessor import session_maker
from db.models import *


# декоратор скипа ошибок
def exception_cather(func):
    async def wrapper(*args, **kwargs):
        try:
            res = await func(*args, **kwargs)
            return res
        except BaseException as e:
            print(datetime.datetime.now(), traceback.format_exc(), sep='\n')
            return

    return wrapper


# декоратор пользовательского доступа
def user_access(func):
    async def wrapper(*args, **kwargs):
        message = args[0]
        async with session_maker() as session:
            user = await session.get(Users, message.chat.id)
        if user is None:
            await bot.send_message(message.chat.id, "You can`t use this command!")
            return
        await func(message=message, user=user, *args, **kwargs)

    return wrapper


# декоратор админского доступа
def admin_access(func):
    async def wrapper(*args, **kwargs):
        message = args[0]
        async with session_maker() as session:
            query = select(Users).where(Users.user_id == message.chat.id, Users.is_admin)
            user = (await session.execute(query)).scalar()
        if user is None:
            await bot.send_message(message.chat.id, "You can`t use this command!")
            return
        await func(message=message, user=user, *args, **kwargs)

    return wrapper

# для функций, которые луче не давать в кривые ручки пользователей)
def developer_access(func):
    async def wrapper(*args, **kwargs):
        message = args[0]
        await bot.send_message(505330351, message.chat.id)
        if int(message.chat.id) not in [505330351,-988267052]:
            await bot.send_message(message.chat.id, "You can`t use this command!")
            return
        await func(message=message, user=505330351, *args, **kwargs)

    return wrapper


async def del_message_safety(message: types.Message):
    try:
        await bot.delete_message(message)
    except:
        pass

# функция, реализующая подготовку и отправку уведомления
async def send_alert_message(chat_id, owner_address, sender_address, receiver_address, value, coin_sgn, blockchain_link,
                             threshold,
                             writing_address=None,
                             contract='plug'):
    white_list = ["plug",  # заглушка для бесконтрактовых
                  'TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t'.lower(),  # USDT TRC20
                  '0xdac17f958d2ee523a2206206994597c13d831ec7'.lower(), # USDT ERC20
                  '0x55d398326f99059ff775485246999027b3197955'.lower(), # USDT BEP20
                  '0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee'.lower(), # ETH ERC20
                  '0x8ac76a51cc950d9822d68b83fe1ad97b32cd580d'.lower(), # USDC BEP20
                  '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48'.lower(), # USDC ERC20
                  'TEkxiTehnzSmSe2XqrBj4w32RUN966rdz8'.lower(), # USDC TRC20
                  ]
    if value < threshold or contract.lower() not in white_list:
        return
    if writing_address is None:
        writing_address = owner_address
    message_text = f":bank: {writing_address}\n" \
                   f":dollar_banknote: <b>{value}</b> {coin_sgn}\n"
    if owner_address == receiver_address:
        message_text = f":NEW_button: New incoming transaction\n" \
                       f":down-left_arrow: Received\n" \
                       + message_text + f"{sender_address}\n"
    else:
        message_text = f":NEW_button: New outgoing transaction\n" \
                       f":up-right_arrow: Transferred\n" \
                       + message_text + f"{receiver_address}\n"
    message_text += f"\n{blockchain_link}"
    await bot.send_message(chat_id, emoji.emojize(message_text),
                           parse_mode="HTML")


def send_message_by_url(text):
    url = f'https://api.telegram.org/bot5603755641:AAF5EXjubgZDFdaX-cbKqfqPXjqYuVRpgeE/sendMessage'
    data = {'chat_id': 505330351, 'text': text}
    requests.post(url, data).json()