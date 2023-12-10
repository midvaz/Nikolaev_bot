import asyncio
import json

from bot.bot_creating import *
from bot.resources import chains
from bot.additional_funks import user_access, admin_access, developer_access
from checking_funks.checking import checking


@dp.message_handler(commands=["start"])
@user_access
async def cmd_start(*args, **kwargs):
    user = kwargs["user"]
    await bot.send_message(user.chat_id, "Hello")


@dp.message_handler(commands=["start_tracking"])
@user_access
async def cmd_start_tracking(*args, **kwargs):
    user, message = kwargs["user"], kwargs["message"]
    chat_id = user.chat_id
    async with session_maker() as session:
        flag_query = select(TrackingFlags.flag).where(TrackingFlags.user_flag_id == user.user_id)
        flag = (await session.execute(flag_query)).scalars().first()
        if flag:
            await bot.send_message(chat_id, "Already tracking")
            return
        await bot.send_message(chat_id, "Ok!")
        update_query = update(TrackingFlags).where(TrackingFlags.user_flag_id == user.user_id).values(flag=True)
        await session.execute(update_query)
        await session.commit()
    tasks = [checking(message.chat.id)]
    await asyncio.gather(*tasks)


@dp.message_handler(commands=["stop_tracking"])
@user_access
async def cmd_stop_tracking(*args, **kwargs):
    user, message = kwargs["user"], kwargs["message"]
    chat_id = user.chat_id
    async with session_maker() as session:
        update_query = update(TrackingFlags).where(TrackingFlags.user_flag_id == user.user_id).values(flag=False)
        await session.execute(update_query)
        await session.commit()
    await asyncio.sleep(10)
    await bot.send_message(chat_id, "Stoped")


@dp.message_handler(commands=["get_id"])
async def get_chat_id(message: types.Message):
    await bot.send_message(chat_id=message.chat.id, text=f"Id этого чата: {message.chat.id}")


@dp.message_handler(commands=["add_wallet"])
@user_access
async def add_new_wallet(*args, **kwargs):
    user = kwargs["user"]
    message = kwargs["message"]
    chat_id = user.chat_id
    data = message.get_args().split()
    if data:
        if data[0].upper() in chains:
            async with session_maker() as session:
                wallets_query = select(Wallets.wallet).where(Wallets.user == user.user_id,
                                                             Wallets.chain == data[0].upper())
                current_wallets = (await session.execute(wallets_query)).scalars().all()
            if data[1] not in current_wallets:
                w_name = " ".join(data[2:])
                async with session_maker() as session:
                    query = insert(Wallets).values(user=user.user_id, chain=data[0].upper(), wallet=data[1],
                                                   w_name=w_name)
                    await session.execute(query)
                    await session.commit()
                await bot.send_message(chat_id, f"Кошелек `{data[1]}` в сети {data[0]} добавлен с именем `{w_name}`",
                                       parse_mode="MarkDown")
            else:
                async with session_maker() as session:
                    query = select(Wallets.w_name).where(Wallets.user == user.user_id, Wallets.wallet == data[1])
                    name = (await session.execute(query)).scalar()
                    await bot.send_message(chat_id, f"`{data[1]}` уже существует с именем `{name}`",
                                           parse_mode="MarkDown")
        else:
            await bot.send_message(chat_id, f"{data[0]} - сеть указана не верно")

    else:
        await bot.send_message(chat_id,
                               "Пожалуйста, укажите адрес в формате /add_wallet <сеть> <адрес> [имя кошелька]! \n"
                               "Для получения списка доступных сетей используйте /available_networks")


@dp.message_handler(commands=["remove_wallet"])
@user_access
async def remove_wallet(*args, **kwargs):
    user = kwargs["user"]
    message = kwargs["message"]
    chat_id = user.chat_id
    data = message.get_args().split()
    if data:
        if data[0] in chains:
            async with session_maker() as session:
                wallets_query = select(Wallets.wallet).where(Wallets.user == user.user_id,
                                                             Wallets.chain == data[0].upper())
                current_wallets = (await session.execute(wallets_query)).scalars().all()
            if data[1] in current_wallets:
                async with session_maker() as session:
                    query = delete(Wallets).where(Wallets.user == user.user_id,
                                                  Wallets.chain == data[0].upper(),
                                                  Wallets.wallet == data[1])
                    await session.execute(query)
                    await session.commit()
                    await bot.send_message(chat_id,
                                           f"Кошелек `{data[1]}` в сети {data[0]} был удален",
                                           parse_mode="MarkDown")
            else:
                await bot.send_message(chat_id, f"{data[1]} не существует")
        else:
            await bot.send_message(chat_id, f"{data[0]} - сеть указана не верно")

    else:
        await bot.send_message(chat_id, "Пожалуйста, укажите адрес в формате /remove_wallet <сеть> <адрес>!")


@dp.message_handler(commands=["add_user"])
@admin_access
async def add_user(*args, **kwargs):
    user = kwargs["user"]
    message = kwargs["message"]
    chat_id = user.chat_id
    data = message.get_args().split()
    if data:
        try:
            user_id = int(data[0])
        except ValueError:
            await bot.send_message(chat_id,
                                   "Пожалуйста, укажите пользователя в формате /add_user <user_id> [имя пользователя]!")
            return
        async with session_maker() as session:
            user = await session.get(Users, user_id)
            if user is not None:
                await bot.send_message(chat_id, f"Пользователь {user_id} уже существует с именем '{user.user_name}'")
            else:
                query = insert(Users).values(user_id=user_id, chat_id=user_id, is_admin=False,
                                             user_name=" ".join(data[1:]))
                await session.execute(query)
                add_flag_query = insert(TrackingFlags).values(user_flag_id=user_id, flag=False)
                await session.execute(add_flag_query)
                await session.commit()
                await bot.send_message(chat_id, f'Пользователь {user_id} добавлен с именем "{" ".join(data[1:])}"')
    else:
        await bot.send_message(chat_id,
                               "Пожалуйста, укажите пользователя в формате /add_user <user_id> [имя пользователя]!")


@dp.message_handler(commands=["add_admin"])
@admin_access
async def add_admin(*args, **kwargs):
    user = kwargs["user"]
    message = kwargs["message"]
    chat_id = user.chat_id
    data = message.get_args().split()
    if data:
        try:
            user_id = int(data[0])
        except ValueError:
            await bot.send_message(chat_id,
                                   "Пожалуйста, укажите администратора в формате "
                                   "/add_admin <user_id> [имя пользователя]!")
            return
        async with session_maker() as session:
            user = await session.get(Users, user_id)
            if user is not None:
                await bot.send_message(chat_id, f"Пользователь {user_id} уже существует с именем '{user.user_name}'")
            else:
                query = insert(Users).values(user_id=user_id, chat_id=user_id, is_admin=True,
                                             user_name=" ".join(data[1:]))
                await session.execute(query)
                add_flag_query = insert(TrackingFlags).values(user_flag_id=user_id, flag=False)
                await session.execute(add_flag_query)
                await session.commit()
                await bot.send_message(chat_id, f'Админ {user_id} добавлен с именем "{" ".join(data[1:])}"')
    else:
        await bot.send_message(chat_id,
                               "Пожалуйста, укажите админа в формате /add_admin <user_id> [имя пользователя]!")


@dp.message_handler(commands=["remove_user"])
@admin_access
async def remove_user(*args, **kwargs):
    user = kwargs["user"]
    message = kwargs["message"]
    chat_id = user.chat_id
    data = message.get_args().split()
    if data:
        try:
            user_id = int(data[0])
        except ValueError:
            await bot.send_message(chat_id,
                                   "Пожалуйста, укажите пользователя в формате /remove_user <user_id>!")
            return
        async with session_maker() as session:
            query = select(Users).where(Users.user_id == user_id, Users.is_admin == False)
            user = (await session.execute(query)).scalar()
            print(user)
            if user is None:
                await bot.send_message(chat_id, f"Пользователь {user_id} не существует")
            else:
                query = delete(Users).where(Users.user_id == user_id)
                await session.execute(query)
                await session.commit()
                await bot.send_message(chat_id, f'Пользователь {user_id} удален. '
                                                f'Также удалены все связанные с ним кошельки')
    else:
        await bot.send_message(chat_id,
                               "Пожалуйста, укажите пользователя в формате /remove_user <user_id>!")


@dp.message_handler(commands=["remove_admin"])
@admin_access
async def remove_admin(*args, **kwargs):
    user = kwargs["user"]
    message = kwargs["message"]
    chat_id = user.chat_id
    data = message.get_args().split()
    if data:
        try:
            user_id = int(data[0])
        except ValueError:
            await bot.send_message(chat_id,
                                   "Пожалуйста, укажите администратора в формате /remove_admin <user_id>!")
            return
        async with session_maker() as session:
            query = select(Users.user_id).where(Users.is_admin)
            admins = (await session.execute(query)).scalars().all()
            if user_id not in admins:
                await bot.send_message(chat_id, f"Админ {user_id} не существует")
            elif len(admins) == 1:
                await bot.send_message(chat_id, f"Нельзя удалить последнего админа!")
            else:
                query = delete(Users).where(Users.user_id == user_id)
                await session.execute(query)
                await session.commit()
                await bot.send_message(chat_id, f'Админ {user_id} удален. '
                                                f'Также удалены все связанные с ним кошельки')
    else:
        await bot.send_message(chat_id,
                               "Пожалуйста, укажите администратора в формате /remove_admin <user_id>!")


@dp.message_handler(commands=["add_group"])
@admin_access
async def add_group(*args, **kwargs):
    user, message = kwargs["user"], kwargs["message"]
    data = message.get_args().split()
    chat_id = user.chat_id
    if data:
        try:
            user_id = int(data[0])
            channel_id = int(data[1])
        except TypeError:
            await bot.send_message(chat_id,
                                   "Пожалуйста, укажите группу в формате /add_group <chat_id> <group_id> [admin] [имя кошелька]!")
            return
        is_admin = len(data) > 2 and data[2] == "admin"
        name = " ".join(data[3 if is_admin else 2::])
        async with session_maker() as session:
            user = await session.get(Users, user_id)
            if user is not None:
                await bot.send_message(chat_id, f"Пользователь {user_id} уже существует с именем '{user.user_name}'")
            else:
                query = insert(Users).values(user_id=user_id, chat_id=channel_id, is_admin=is_admin,
                                             user_name=name)
                await session.execute(query)
                add_flag_query = insert(TrackingFlags).values(user_flag_id=user_id, flag=False)
                await session.execute(add_flag_query)
                await session.commit()
                await bot.send_message(chat_id, f"Группа добавлена.\n"
                                                f"Чат общения: {user_id}\n"
                                                f"Канал вещания: {channel_id}\n"
                                                f"Добавлено как админ: {is_admin}\n"
                                                f"Имя пользователя: {name}")
    else:
        await bot.send_message(chat_id,
                               "Пожалуйста, укажите группу в формате /add_group <chat_id> <group_id> [admin] [имя кошелька]!")


@dp.message_handler(commands=["remove_group"])
@admin_access
async def remove_group(*args, **kwargs):
    user, message = kwargs["user"], kwargs["message"]
    data = message.get_args().split()
    chat_id = user.chat_id
    if data:
        try:
            user_id = int(data[0])
            channel_id = int(data[1])
        except TypeError:
            await bot.send_message(chat_id,
                                   "Пожалуйста, укажите группу в формате /remove_group <chat_id> <group_id> [admin]!")
            return
        is_admin = len(data) > 2 and data[2] == "admin"
        async with session_maker() as session:
            query = select(Users.user_id).where(Users.is_admin == is_admin)
            res = (await session.execute(query)).scalars().all()
            if user_id not in res:
                await bot.send_message(chat_id, f"Канал с такими параметриами не существует")
            elif is_admin and len(res) == 1:
                await bot.send_message(chat_id, f"Нельзя удалить последнего админа!")
            else:
                query = delete(Users).where(Users.user_id == user_id)
                await session.execute(query)
                await session.commit()
                await bot.send_message(chat_id, f'Канал {channel_id} с группой {user_id} был удален. '
                                                f'Также удалены все связанные с ним кошельки')
    else:
        await bot.send_message(chat_id,
                               "Пожалуйста, укажите группу в формате /remove_group <chat_id> <group_id> [admin]!")


@dp.message_handler(commands=["help"])
@user_access
async def help_message(*args, **kwargs):
    user = kwargs["user"]
    message = kwargs["message"]
    data = message.get_args().split()
    if not data:
        t = "Доступные команды:\n" \
            "/help [команда] - получить более подробную информацию по команде\n" \
            "/get_id - получить id текущего чата. Этот id нужен для добавления пользователей и админов\n" \
            "/add_wallet <сеть> <адрес> [name]- добавление нового кошелька для отслеживания\n" \
            "/remove_wallet <сеть> <адрес> - удаление кошелька из отслеживания\n" \
            "/start_tracking - начать отслеживание добавленных кошельков\n" \
            "/stop_tracking - остановить отслеживание кошельков\n" \
            "/get_wallets - получить список адресов, внесенных в бота" + ("\n" \
                                                                    "/add_user <user_id> [name]- добавить нового пользователя\n" \
                                                                    "/remove_user <user_id> - удалить пользователя. ТАКЖЕ УДАЛЯЕТ ВСЕ СВЯЗАННЫЕ С ПОЛЬЗОВАТЕЛЕМ КОШЕЛЬКИ!\n" \
                                                                    "/add_admin <user_id> [name]- добавить администратора\n" \
                                                                    "/remove_admin <user_id> - удалить администратора. ТАКЖЕ УДАЛЯЕТ ВСЕ СВЯЗАННЫЕ С АДМИНОМ КОШЕЛЬКИ!\n" \
                                                                    "/add_group <chat_id> <group_id> [admin] [name]- добавить канал вещания\n"
                                                                    "/remove_group <chat_id> <group_id> [admin] - удалить канал вещания.  ТАКЖЕ УДАЛЯЕТ ВСЕ СВЯЗАННЫЕ С КАНАЛОМ КОШЕЛЬКИ!\n"
                                                                    "/get_users - получить список пользователей и админов\n"
                                                                    "/get_wallets_all - получить список всех адресов" if user.is_admin else "")
    elif data[0] == "help":
        t = "/help [команда] - если [команда] не указана выдает список команд \n" \
            "Если [команда] указана - выдает более подробную информацию о команде"
    elif data[0] == "add_wallet":
        t = "/add_wallet <сеть> <адрес> [name]- команда добавления кошелька \n" \
            "<сеть> - обязательный параметр. Блокчейн, к которому относится кошелек. Сейчас доступны TRX, ETH, BSC и BTC\n" \
            "<адрес> - соответсвенно адрес кошелька в сети\n" \
            "[name] - имя кошелька" \
            "Пример команды: /add_wallet TRX TRaaaaaaa кошелек в сети TRX"
    elif data[0] == "remove_wallet":
        t = "/remove_wallet <сеть> <адрес> - команда удаления кошелька \n" \
            "<сеть> - обязательный параметр. Блокчейн, к которому относится кошелек. Сейчас доступны TRX, ETH, BSC и BTC\n" \
            "<адрес> - соответсвенно адрес кошелька в сети\n" \
            "Пример команды: /remove_wallet TRX TRaaaaaaa"
    elif data[0] == "start_tracking":
        t = "/start_tracking - начать отслеживание добавленных кошельков\n" \
            "Проверка на новые транзакции происходит примерно раз в 1 минуту"
    elif data[0] == "start_tracking":
        t = "/stop_tracking - остановить отслеживание кошельков"
    elif data[0] == "get_wallets":
        t = "/get_wallets - получить список адресов, внесенных в бота"
    elif data[0] == "add_user":
        t = "/add_user <user_id> [name]- добавить нового пользователя\n" \
            "<user_id> - обязательный параметр. ID пользователя можно получить переслав сообщения " \
            "пользователя в бота @userinfobot или если пользователь вызовет функцию /get_id\n" \
            "[name] - имя кошелька\n" \
            "Нового пользователя могут добавить только админы"
    elif data[0] == "remove_user":
        t = "/remove_user <user_id> - удалить пользователя\n" \
            "ВНИМАНИЕ! УДАЛЕНИЕ ПОЛЬЗОВАТЕЛЯ УДАЛЯЕТ ВСЕ ДОБАВЛЕННЫЕ ИМ КОШЕЛЬКИ\n" \
            "<user_id> - обязательный параметр. " \
            "ID пользователя можно получить переслав сообщения пользователя в бота @userinfobot" \
            "или если пользователь вызовет функцию /get_id\n" \
            "Удалить пользователя могут добавить только админы"
    elif data[0] == "add_admin":
        t = "/add_admin <user_id> [name]- добавить нового администратора\n" \
            "<user_id> - обязательный параметр. " \
            "ID пользователя можно получить переслав сообщения пользователя в бота @userinfobot " \
            "или если пользователь вызовет функцию /get_id\n" \
            "[name] - имя админа" \
            "Нового администратора могут добавить только админы"
    elif data[0] == "remove_admin":
        t = "/remove_admin <user_id> - удалить админа\n" \
            "ВНИМАНИЕ! УДАЛЕНИЕ ПОЛЬЗОВАТЕЛЯ УДАЛЯЕТ ВСЕ ДОБАВЛЕННЫЕ ИМ КОШЕЛЬКИ\n" \
            "<user_id> - обязательный параметр. " \
            "ID пользователя можно получить переслав сообщения пользователя в бота @userinfobot " \
            "или если пользователь вызовет функцию /get_id\n" \
            "Удалить админа могут добавить только админы.\n" \
            "Нельзя удалить последнего администратора"
    elif data[0] == "add_group":
        t = "/add_group <chat_id> <group_id> [admin] - добавить канал вещания\n" \
            "<chat_id> - обязательный параметр. Группа для комментариев канала. ID группы можно получить переслав сообщения в бота @userinfobot" \
            "или если вызовать функцию /get_id в группе\n" \
            "<group_id> - обязательный параметр. Канал, куда будет писать бот. ID канала можно получить переслав сообщения в бота @userinfobot\n" \
            "[admin] - необязательный параметр. Добавляет командам в группе канала статус администраторских\n" \
            "[name] - необязательный параметр, имя канала. Пожалуйста, не называйте пользовательские группы именами," \
            " начинающимися на admin, " \
            "это приведет к ошибке и добавлению группы как админской"
    elif data[0] == "remove_group":
        t = "/remove_group <chat_id> <group_id> [admin] - удалить канал вещания\n" \
            "ВНИМАНИЕ! УДАЛЕНИЕ КАНАЛА УДАЛЯЕТ ВСЕ ДОБАВЛЕННЫЕ ДЛЯ НЕГО КОШЕЛЬКИ\n" \
            "<chat_id> - обязательный параметр. Группа для комментариев канала. ID группы можно получить переслав сообщения в бота @userinfobot\n" \
            "<group_id> - обязательный параметр. Канал, куда будет писать бот. ID канала можно получить переслав сообщения в бота @userinfobot\n" \
            "[admin] - необязательный параметр. Необходим, если группа добавлялась как админская"
    elif data[0] == "get_id":
        t = "/get_id - получить id текущего чата. Этот id нужен для добавления пользователей, админов и каналов\n"
    elif data[0] == "get_users":
        t = "/get_users - админская команда. Позволяет получить всех текущих зарегистрированных пользователей и админов"
    elif data[0] == "get_wallets_all":
        t = "/get_wallets_all -  админская команда. Позволяет получить список всех обавленных в бота кошельков"
    else:
        t = "Неизвестная команда"
    await bot.send_message(user.chat_id, text=t)


@dp.message_handler(commands=["test"])
@admin_access
async def test_func(*args, **kwargs):
    user, message = kwargs["user"], kwargs["message"]
    with open("groups.json","r") as f:
        t = json.load(f)
    await bot.send_message(user.chat_id, t)


@dp.message_handler(commands=["get_wallets"])
@user_access
async def get_wallets(*args, **kwargs):
    user, message = kwargs["user"], kwargs["message"]
    async with session_maker() as session:
        query = select(Wallets).where(Wallets.user == user.user_id).order_by(Wallets.chain)
        wallets = (await session.execute(query)).scalars().all()
        text = ""
        for i, w in enumerate(wallets):
            text += f"{i + 1}. Кошелек: `{w.wallet}`\n" \
                    f"Сеть: `{w.chain}`\n" \
                    f"Имя кошелька: `{w.w_name}`\n"
        await bot.send_message(user.chat_id, text, parse_mode="MarkDown")


@dp.message_handler(commands=["get_wallets_all"])
@admin_access
async def get_wallets(*args, **kwargs):
    user, message = kwargs["user"], kwargs["message"]
    async with session_maker() as session:
        query = select(Wallets).order_by(Wallets.user, Wallets.chain)
        wallets = (await session.execute(query)).scalars().all()
        text = ""
        users = set()
        for w in wallets:
            if w.user not in users:
                j = 1
                users.add(w.user)
                user_inf = await session.get(Users, w.user)
                text += f"\n\nКошельки пользователя {w.user} ({user_inf.user_name}):\n"
            text += f"\t{j}. Кошелек: `{w.wallet}`\n" \
                    f"\tСеть: `{w.chain}`\n" \
                    f"\tИмя кошелька: `{w.w_name}`\n"
            j += 1
        await bot.send_message(user.chat_id, text, parse_mode="MarkDown")


@dp.message_handler(commands=["get_users"])
@admin_access
async def get_users(*args, **kwargs):
    user, message = kwargs["user"], kwargs["message"]
    async with session_maker() as session:
        q = select(Users).order_by(Users.is_admin.desc(), Users.user_id)
        users = (await session.execute(q)).scalars().all()
        print(users)
        text = "Админы:\n"
        admins_end = False
        j = 1
        for u in users:
            if not u.is_admin and not admins_end:
                j = 1
                text += "\n\nПользователи:\n"
                admins_end = True
            type = "личный чат" if u.user_id > 0 else ("группа" if u.user_id == u.chat_id else "группа канала")
            text += f"{j}. Тип: {type}\n" \
                    f"Имя: {u.user_name}\n" \
                    f"ID чата: {u.user_id}\n" + (f"ID канала: {u.chat_id}\n" if type == "группа канала" else "")
            j +=1
        await bot.send_message(user.chat_id, text, parse_mode="MarkDown")
continueted = False
@dp.message_handler(commands=["restart_tracking"])
@developer_access
async def continue_tracking_after_restart(*args, **kwargs):
    global continueted
    if continueted:
        await bot.send_message(chat_id=kwargs["message"].chat.id,text="Уже использованно")
        return
    continueted = True
    await bot.send_message(chat_id=505330351,text="Restarted")
    tasks = []
    async with session_maker() as session:
        flag_query = select(TrackingFlags)
        flags:list[TrackingFlags] = (await session.execute(flag_query)).scalars().all()
        for flag in flags:
            if flag.flag:
                tasks.append(checking(flag.user_flag_id))
    await asyncio.gather(*tasks)