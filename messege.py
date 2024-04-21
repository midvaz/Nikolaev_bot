messege_help = {
    '/help': "Доступные команды:\n" \
            "/help [команда] - получить более подробную информацию по команде\n" \
            "/get_id - получить id текущего чата. Этот id нужен для добавления пользователей и админов\n" \
            "/add_wallet <сеть> <адрес> [name]- добавление нового кошелька для отслеживания\n" \
            "/remove_wallet <сеть> <адрес> - удаление кошелька из отслеживания\n" \
            "/start_tracking - начать отслеживание добавленных кошельков\n" \
            "/stop_tracking - остановить отслеживание кошельков\n" \
            "/get_wallets - получить список адресов, внесенных в бота"
    ,'/help help': "/help [команда] - если [команда] не указана выдает список команд \n" \
                    "Если [команда] указана - выдает более подробную информацию о команде"
    ,'/help add_wallet': "/add_wallet <сеть> <адрес> [name]- команда добавления кошелька \n" \
                        "<сеть> - обязательный параметр. Блокчейн, к которому относится кошелек. Сейчас доступны TRX, ETH, BSC и BTC\n" \
                        "<адрес> - соответсвенно адрес кошелька в сети\n" \
                        "[name] - имя кошелька" \
                        "Пример команды: /add_wallet TRX TRaaaaaaa кошелек в сети TRX"
    ,'/help remove_wallet': "/remove_wallet <сеть> <адрес> - команда удаления кошелька \n" \
                            "<сеть> - обязательный параметр. Блокчейн, к которому относится кошелек. Сейчас доступны TRX, ETH, BSC и BTC\n" \
                            "<адрес> - соответсвенно адрес кошелька в сети\n" \
                            "Пример команды: /remove_wallet TRX TRaaaaaaa"
    ,'/help start_tracking': "/start_tracking - начать отслеживание добавленных кошельков\n" \
                            "Проверка на новые транзакции происходит примерно раз в 1 минуту"
    ,'/help stop_tracking': "/stop_tracking - остановить отслеживание кошельков"
    ,'/help get_wallets': "/get_wallets - получить список адресов, внесенных в бота"
    ,'/help add_user': "/add_user <user_id> [name]- добавить нового пользователя\n" \
                        "<user_id> - обязательный параметр. ID пользователя можно получить переслав сообщения " \
                        "пользователя в бота @userinfobot или если пользователь вызовет функцию /get_id\n" \
                        "[name] - имя кошелька\n" \
                        "Нового пользователя могут добавить только админы"
    ,'/help remove_user': "/remove_user <user_id> - удалить пользователя\n" \
                            "ВНИМАНИЕ! УДАЛЕНИЕ ПОЛЬЗОВАТЕЛЯ УДАЛЯЕТ ВСЕ ДОБАВЛЕННЫЕ ИМ КОШЕЛЬКИ\n" \
                            "<user_id> - обязательный параметр. " \
                            "ID пользователя можно получить переслав сообщения пользователя в бота @userinfobot" \
                            "или если пользователь вызовет функцию /get_id\n" \
                            "Удалить пользователя могут добавить только админы"
    ,'/help add_admin': "/add_admin <user_id> [name]- добавить нового администратора\n" \
            "<user_id> - обязательный параметр. " \
            "ID пользователя можно получить переслав сообщения пользователя в бота @userinfobot " \
            "или если пользователь вызовет функцию /get_id\n" \
            "[name] - имя админа" \
            "Нового администратора могут добавить только админы"
    ,'/help remove_admin': "/remove_admin <user_id> - удалить админа\n" \
            "ВНИМАНИЕ! УДАЛЕНИЕ ПОЛЬЗОВАТЕЛЯ УДАЛЯЕТ ВСЕ ДОБАВЛЕННЫЕ ИМ КОШЕЛЬКИ\n" \
            "<user_id> - обязательный параметр. " \
            "ID пользователя можно получить переслав сообщения пользователя в бота @userinfobot " \
            "или если пользователь вызовет функцию /get_id\n" \
            "Удалить админа могут добавить только админы.\n" \
            "Нельзя удалить последнего администратора"
    ,'/help add_group': "/add_group <chat_id> <group_id> [admin] - добавить канал вещания\n" \
                        "<chat_id> - обязательный параметр. Группа для комментариев канала. ID группы можно получить переслав сообщения в бота @userinfobot" \
                        "или если вызовать функцию /get_id в группе\n" \
                        "<group_id> - обязательный параметр. Канал, куда будет писать бот. ID канала можно получить переслав сообщения в бота @userinfobot\n" \
                        "[admin] - необязательный параметр. Добавляет командам в группе канала статус администраторских\n" \
                        "[name] - необязательный параметр, имя канала. Пожалуйста, не называйте пользовательские группы именами," \
                        " начинающимися на admin, " \
                        "это приведет к ошибке и добавлению группы как админской"
    ,'/help remove_group': "/remove_group <chat_id> <group_id> [admin] - удалить канал вещания\n" \
                            "ВНИМАНИЕ! УДАЛЕНИЕ КАНАЛА УДАЛЯЕТ ВСЕ ДОБАВЛЕННЫЕ ДЛЯ НЕГО КОШЕЛЬКИ\n" \
                            "<chat_id> - обязательный параметр. Группа для комментариев канала. ID группы можно получить переслав сообщения в бота @userinfobot\n" \
                            "<group_id> - обязательный параметр. Канал, куда будет писать бот. ID канала можно получить переслав сообщения в бота @userinfobot\n" \
                            "[admin] - необязательный параметр. Необходим, если группа добавлялась как админская"
    ,'/help get_id': "/get_id - получить id текущего чата. Этот id нужен для добавления пользователей, админов и каналов\n"
    ,'/help get_users': "/get_users - админская команда. Позволяет получить всех текущих зарегистрированных пользователей и админов"
    ,'/help get_wallets_all': "/get_wallets_all -  админская команда. Позволяет получить список всех обавленных в бота кошельков"
        
}