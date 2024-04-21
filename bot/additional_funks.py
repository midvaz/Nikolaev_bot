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
from config import ID_G, ID_CHANEL, WHITE_LIST, TOKEN

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
            try:
                user = await session.get(Users, message.chat.id)
            except Exception as er:
                print(er)
        if user is None:
            await bot.send_message(message.chat.id, f"You can`t use this command! {message.chat.id}")
            print(f"You can`t use this command! {message.chat.id}")
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
        await bot.send_message(ID_G, message.chat.id)
        if int(message.chat.id) not in [ID_G,ID_CHANEL]:
            await bot.send_message(message.chat.id, "You can`t use this command!")
            return
        await func(message=message, user=ID_G, *args, **kwargs)
    print("Что-то написали в канал")
    return wrapper


async def del_message_safety(message: types.Message):
    try:
        await bot.delete_message(message)
    except:
        pass

# функция, реализующая подготовку и отправку уведомления
async def send_alert_message(
    chat_id, 
    owner_address, 
    sender_address, 
    receiver_address, 
    value, 
    coin_sgn, 
    blockchain_link,
    threshold,
    writing_address=None,
    contract='plug'
):
    if value < threshold or contract.lower() not in WHITE_LIST:
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
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
    data = {'chat_id': ID_G, 'text': text}
    requests.post(url, data).json()