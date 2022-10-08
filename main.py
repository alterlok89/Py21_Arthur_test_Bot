from aiogram import Bot, Dispatcher, executor, types
import os
import sqlite3


class DataBase:
    def __init__(self, db_name: str):
        self.__db_name = f'{db_name}.sqlite'
        self.__conn = sqlite3.connect(self.__db_name)

    def setup(self, table: str, data: dict):
        keys = list(data.keys())
        values = list(data.values())
        # print(keys)
        # print(values)
        req = f'CREATE TABLE IF NOT EXISTS "{table}"('
        for i in range(len(keys)):
            req += f'"{keys[i]}" {values[i]}, '
        req = req[:-2] + ')'
        # print(req)
        self.__conn.cursor()
        self.__conn.execute(req)
        self.__conn.commit()

    def add_item(self, table: str, data: dict):
        # print(data, ' - функция класса')
        columns = ''
        values = ''
        curs = self.__conn.cursor()
        select = curs.execute(f"SELECT user_id FROM Users WHERE user_id={list(data.values())[0]}",)
        # print(select.fetchone())
        select_data = select.fetchone()
        # print(a)
        if select_data is None:
            for i in range(len(data.keys())):
                columns += f'"{list(data.keys())[i]}", '
                values += f'"{list(data.values())[i]}", '
            columns = columns[:-2]
            values = values[:-2]

            req = f'INSERT INTO "{table}"' \
                                f' ({columns}) ' \
                                f'VALUES ' \
                                f'({values});'
            print(req)
            self.__conn.cursor()
            self.__conn.execute(req)
            self.__conn.commit()
        else:
            print(f'Пользователь с user_id: {list(data.values())[0]} уже существует!')

    def delete_table(self, table: str,):
        req = f'DROP TABLE IF EXISTS "{table}"'
        self.__conn.cursor()
        self.__conn.execute(req)
        self.__conn.commit()


db = DataBase('Users Bot Base')
db.setup(table='Users',
               data={
                    'id': 'integer primary key autoincrement',
                    'telegram_id': 'integer primary key',
                    'first_name': 'string',
                    'last_name': 'string',
                    'username': 'string not null',
                    'is_bot': 'string not null',
                    'language_code': 'string not null',
                })

TOKEN = os.environ['token']
# print(TOKEN)
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

users = {}


@dp.message_handler()
async def echo(message: types.Message):
    print(message)
    user = {
                'telegram_id': f'{message.from_user.id}',
                'first_name': f'{message.from_user.first_name}',
                'last_name': f'{message.from_user.last_name}',
                'username': f'{message.from_user.username}',
                'is_bot': f'{message.from_user.is_bot}',
                'language_code': f'{message.from_user.language_code}',
                }
    # print(user)
    users.update({message.from_user.id: {message.from_user.first_name: message.from_user.username}})
    # await message.answer(message.text)
    # await message.reply(message.text)
    text = f'Пользователь со следующими данными написал в чат!\n' \
           f'telegram_id: {message.from_user.id}\n' \
           f'first_name: {message.from_user.first_name}\n' \
           f'last_name: {message.from_user.last_name}\n' \
           f'username: {message.from_user.username}\n' \
           f'is_bot: {message.from_user.is_bot}\n' \
           f'language_code: {message.from_user.language_code}\n' \
           f'Приветствую!!!'
    # print(text)
    for i in users.keys():
        # print(i)
        await bot.send_message(chat_id=i,
                                text=text)
        if i != message.from_user.id:
            alert = f'Пользователь:\n' \
                    f'ID - {message.from_user.id}\n' \
                    f'FirstName - {message.from_user.first_name}\n' \
                    f'UserNane - {message.from_user.username}\n' \
                    f'Написал сообщение: {message.text}'
            await bot.send_message(chat_id=i,
                                   text=alert)

    db.add_item(table='Users', data=user)


if __name__ == '__main__':
    executor.start_polling(dp)

