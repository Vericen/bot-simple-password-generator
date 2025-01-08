
# version simplepgbot - 1.0
# https://github.com/Vericen/bot-simple-password-generator

import asyncio
import logging
import sys
import random
import string
import json
import os

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, html, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart # Command
from aiogram.types import Message,  CallbackQuery #InlineKeyboardMarkup, InlineKeyboardButton, MenuButtonCommands
from aiogram.utils.keyboard import InlineKeyboardBuilder #ReplyKeyboardBuilder

load_dotenv()

unreg_user_message = "Перед началом моего использования воспользуйся командой /start хотя бы один раз, чтобы я мог запоминать параметры генерации паролей ^-^"
start_second_message = "Я очень простой генератор для паролей, созданный @vericen в качестве практики первого скрипта на Python, у меня ты можешь генерировать себе безопасные пароли в любое время, а мой исходный код находится здесь: \nhttps://github.com/Vericen/bot-simple-password-generator\n\n{html.bold(Мои команды:)}\n/gen - {html.italic(Сгенерировать новый пароль)}\n/config - {html.italic(Изменить параметры генерации пароля"
token = os.getenv("BOT_TOKEN")
db = "set.json"

print("=======================================")
print(" TG Generator Password by Vericen v1.0")
print("     my first script on python >_<")
print("=======================================")

class Passgen:
  def __init__(self, length_pass, numbers, symbols):
      self.length_pass = length_pass
      self.characters = string.ascii_letters
      if numbers == True:
          self.characters = self.characters + string.digits
      if symbols == True:
          self.characters = self.characters + string.punctuation
      self.password = ''.join(random.choice(self.characters) for _ in range(length_pass))

  def generate_password(self):
      password = ''.join(random.choice(self.characters) for _ in range(self.length_pass))
      return password

def load_database():
    if os.path.exists(db):
        with open(db, "r") as file:
            content = file.read().strip()
            if content:
                data = json.loads(content)
                return {k: v for k, v in data.items()} #функция удаления дубликатов
            else:
                return {}
    return {}

def save_database(database):
    with open(db, "w") as file:
        json.dump(database, file, indent=4)

def update_user_settings(user_id, length_pass, numbers, symbols):
    database = load_database()
    database[user_id] = {"length_pass": length_pass, "numbers": numbers, "symbols": symbols}
    save_database(database)

def add_user_to_database(user_id, length_pass=16, numbers=True, symbols=False):
    update_user_settings(user_id, length_pass, numbers, symbols)

dp = Dispatcher()

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    user_id = message.from_user.id
    db = load_database()

    if str(user_id) in db:
        print(f"DB:{user_id} в базе данных, пропускаем")
        await message.answer(
          f"Рад видеть тебя вновь, {html.bold(message.from_user.full_name)}! Я очень простой генератор для паролей, созданный @vericen в качестве практики первого скрипта на Python. "
          f"У меня ты можешь генерировать себе безопасные пароли в любое время, а мой исходный код находится здесь:\n"
          f"https://github.com/Vericen/bot-simple-password-generator\n\n"
          f"{html.bold('Мои команды:')}\n"
          f"/gen - {html.italic('Сгенерировать новый пароль')}\n"
          f"/config - {html.italic('Изменить параметры генерации пароля')}"
)
    else:
        length_pass = 16
        numbers = True
        symbols = False
        add_user_to_database(user_id, length_pass, numbers, symbols)
        await message.answer(
          f"Привет, {html.bold(message.from_user.full_name)}! Я очень простой генератор для паролей, созданный @vericen в качестве практики первого скрипта на Python. "
          f"У меня ты можешь генерировать себе безопасные пароли в любое время, а мой исходный код находится здесь:\n"
          f"https://github.com/Vericen/bot-simple-password-generator\n\n"
          f"{html.bold('Мои команды:')}\n"
          f"/gen - {html.italic('Сгенерировать новый пароль')}\n"
          f"/config - {html.italic('Изменить параметры генерации пароля')}"
)

@dp.message(lambda message: message.text.lower() == "ген" or message.text.startswith('/gen'))
async def cmd_gen(
        message: Message
):
    user_id = message.from_user.id
    db = load_database()
    if str(user_id) in db:
        user_data = db[str(user_id)]
        length_pass = user_data["length_pass"]
        numbers = user_data["numbers"]
        symbols = user_data["symbols"]
    else:
        await message.answer(unreg_user_message)
        return

    try:
        if length_pass > 128:
            await message.answer(f"Максимальная длинна пароля - 128")
            return
        else:
          db = load_database()
          user_data = db[str(user_id)]
          length_pass = user_data["length_pass"]
          numbers = user_data["numbers"]
          symbols = user_data["symbols"]

          password_generator = Passgen(length_pass=length_pass, numbers=numbers, symbols=symbols)

          generated_password = password_generator.generate_password()
          cleared_password = html.quote(generated_password)

          await message.answer(f"Ваш сгенерированный пароль:\n{html.code(cleared_password)}")

    except (IndexError, ValueError):
        await message.answer(
            "Ошибка\n"
            "Index/Value"
        )

@dp.message(lambda message: message.text.lower() == "конфиг" or message.text.startswith('/config'))
async def settings_handler(message: Message):
    user_id = message.from_user.id
    db = load_database()

    if str(user_id) not in db:
        await message.answer(unreg_user_message)
        return

    user_data = db[str(user_id)]

    builder = InlineKeyboardBuilder()
    builder.button(
        text=f"🔢 {'✅' if user_data['numbers'] else '❌'}",
        callback_data="toggle_numbers"
    )
    builder.button(
        text=f"🔣 {'✅' if user_data['symbols'] else '❌'}",
        callback_data="toggle_symbols"
    )
    builder.button(
        text=f"📏 {user_data['length_pass']}",
        callback_data="edit_length"
    )

    keyboard = builder.as_markup()

    sent_message = await message.answer(
        "⚙️ Изменение параметров генерации пароля:",
        reply_markup=keyboard
    )

    keyboard = builder.as_markup()

@dp.callback_query(lambda callback: callback.data in ["toggle_numbers", "toggle_symbols", "edit_length", "generate_password"])
async def callback_handler(callback: types=CallbackQuery):
    user_id = callback.from_user.id

    if callback.data == "toggle_numbers":
        db = load_database()
        user_data = db[str(user_id)]
        length_pass = user_data["length_pass"]
        symbols = user_data["symbols"]
        current_value = db[str(user_id)]["numbers"]
        new_numbers = not current_value
        update_user_settings(user_id, length_pass=length_pass, numbers=new_numbers, symbols=symbols)
        await callback.answer(f"Числа теперь {'включены ✅' if new_numbers else 'выключены ❌'}")
    elif callback.data == "toggle_symbols":
        db = load_database()
        user_data = db[str(user_id)]
        length_pass = user_data["length_pass"]
        numbers = user_data["numbers"]
        current_value = db[str(user_id)]["symbols"]
        new_symbols = not current_value
        update_user_settings(user_id, length_pass=length_pass, numbers=numbers, symbols=new_symbols)
        await callback.answer(f"Символы теперь {'включены ✅' if new_symbols else 'выключены ❌'}")
    elif callback.data == "edit_length":
        await callback.message.answer("📏 Введите новую длину пароля (6-128):")
        await callback.answer()

@dp.message(lambda message: message.text.isdigit())
async def set_length(message: Message):
    user_id = message.from_user.id
    db = load_database()
    user_data = db[str(user_id)]
    new_length = int(message.text)
    numbers = user_data["numbers"]
    symbols = user_data["symbols"]
    if 6 <= new_length <= 128:
        update_user_settings(user_id, length_pass=new_length, numbers=numbers, symbols=symbols)
        await message.answer(f"✅ Длина пароля изменена на {new_length}.")
    else:
        await message.answer("❌ Укажите число от 6 до 128")

async def main() -> None:
    bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
