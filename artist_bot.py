import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta
import asyncio
import csv
from io import StringIO

# Загружаем переменные окружения
load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")  # <-- СЮДА ВСТАВИМ ID ТАБЛИЦЫ ПОЗЖЕ

# Подключаем Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets",
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

import json
from io import StringIO
import os

google_key = json.loads(os.getenv('GOOGLE_KEY'))
google_key_file = StringIO(json.dumps(google_key))

creds = ServiceAccountCredentials.from_json_keyfile_dict(google_key, scope)
client = gspread.authorize(creds)

# Инициализация бота
bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())


# FSM (Finite State Machine) для пошагового ввода данных
class ArtistForm(StatesGroup):
    name = State()
    telegram = State()
    instagram = State()
    phone = State()
    email = State()
    style = State()
    level = State()
    priority = State()
    comment = State()
class SendBitoForm(StatesGroup):
    name = State()
    beats = State()
    reaction = State()

async def clean_prev_message(message: Message, data: dict, state: FSMContext):
    if "last_bot_message" in data:
        try:
            await bot.delete_message(chat_id=message.chat.id, message_id=data['last_bot_message'])
        except:
            pass

    try:
        await message.delete()
    except:
        pass


async def clean_chat(message: Message, state: FSMContext):
    try:
        # Удаляем все последние сообщения, если они были
        data = await state.get_data()
        if "last_bot_message" in data:
            try:
                await bot.delete_message(chat_id=message.chat.id, message_id=data['last_bot_message'])
            except:
                pass

        # Чистим состояние (на всякий случай)
        await state.clear()

        # Удаляем САМУ КОМАНДУ от юзера
        await message.delete()

    except:
        pass


# Команда старт
from aiogram.filters import CommandStart

@dp.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("🔥 Добро пожаловать в твою личную CRM для битмейкера!\n\n"
                         "🚀 Основные команды:\n"
                         "➕ /add – Добавить артиста\n"
                         "📋 /mylist – Моя база артистов\n"
                         "🔎 /search [запрос] – Поиск по базе\n"
                         "📊 /stats – Статистика\n"
                         "🏆 /top /potential /cold – Фильтры по приоритетам\n"
                         "📄 /artist [имя] – Карточка артиста\n\n"
                         "🎼 Работа с битами и сделками:\n"
                         "📤 /send [имя] – Фиксировать отправку битов\n"
                         "💸 /deal [имя сумма] – Зафиксировать сделку\n"
                         "⏰ /remindme [имя] – Поставить напоминание\n"
                         "📞 /contact [имя] – Обновить контакт\n\n"
                         "⚙️ Инструменты:\n"
                         "📁 /export – Выгрузить базу (CSV)\n"
                         "🏅 /score – Баллы активности\n"
                         "🪜 /checkpoint [имя этап] – Этапы по артисту\n"
                         "✏️ /edit [имя поле значение] – Редактировать\n\n"
                         "💬 Если есть вопросы или идеи – пиши сюда @sabbeatsmgmt!")

# Команда добавления артиста
@dp.message(Command("add"))
async def add_artist(message: Message, state: FSMContext):
    await clean_chat(message, state)

    await state.set_state(ArtistForm.name)
    msg = await message.answer("Как зовут артиста?")
    await state.update_data(last_bot_message=msg.message_id)


@dp.message(ArtistForm.name)
async def process_name(message: Message, state: FSMContext):
    data = await state.get_data()
    await clean_prev_message(message, data, state)

    await state.update_data(name=message.text)
    await state.set_state(ArtistForm.telegram)
    msg = await message.answer("Скинь его телегу (@username):")
    await state.update_data(last_bot_message=msg.message_id)


@dp.message(ArtistForm.telegram)
async def process_telegram(message: Message, state: FSMContext):
    data = await state.get_data()
    await clean_prev_message(message, data, state)

    await state.update_data(telegram=message.text)
    await state.set_state(ArtistForm.instagram)
    msg = await message.answer("Скинь его инсту (@username):")
    await state.update_data(last_bot_message=msg.message_id)


@dp.message(ArtistForm.instagram)
async def process_instagram(message: Message, state: FSMContext):
    data = await state.get_data()
    await clean_prev_message(message, data, state)

    await state.update_data(instagram=message.text)
    await state.set_state(ArtistForm.phone)
    msg = await message.answer("Номер телефона?")
    await state.update_data(last_bot_message=msg.message_id)


@dp.message(ArtistForm.phone)
async def process_phone(message: Message, state: FSMContext):
    data = await state.get_data()
    await clean_prev_message(message, data, state)

    await state.update_data(phone=message.text)
    await state.set_state(ArtistForm.email)
    msg = await message.answer("Почта?")
    await state.update_data(last_bot_message=msg.message_id)


@dp.message(ArtistForm.email)
async def process_email(message: Message, state: FSMContext):
    data = await state.get_data()
    await clean_prev_message(message, data, state)

    await state.update_data(email=message.text)
    await state.set_state(ArtistForm.style)

    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Yeat"), KeyboardButton(text="Dark")],
                  [KeyboardButton(text="New Jazz"), KeyboardButton(text="Melodic")],
		  [KeyboardButton(text="BoomBap"), KeyboardButton(text="Plugg")],
		  [KeyboardButton(text="Drill"), KeyboardButton(text="West Coast")]],
        resize_keyboard=True,
        one_time_keyboard=True
    )

    msg = await message.answer("Стиль?", reply_markup=kb)
    await state.update_data(last_bot_message=msg.message_id)


@dp.message(ArtistForm.style)
async def process_style(message: Message, state: FSMContext):
    data = await state.get_data()
    await clean_prev_message(message, data, state)

    await state.update_data(style=message.text)
    await state.set_state(ArtistForm.level)

    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Новичок"), KeyboardButton(text="Средний")],
                  [KeyboardButton(text="Известный")]],
        resize_keyboard=True,
        one_time_keyboard=True
    )

    msg = await message.answer("Уровень?", reply_markup=kb)
    await state.update_data(last_bot_message=msg.message_id)


@dp.message(ArtistForm.level)
async def process_level(message: Message, state: FSMContext):
    data = await state.get_data()
    await clean_prev_message(message, data, state)

    await state.update_data(level=message.text)
    await state.set_state(ArtistForm.priority)

    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🔥 ТОП"), KeyboardButton(text="💸 ПОТЕНЦИАЛ")],
                  [KeyboardButton(text="❄️ ХОЛОДНЫЙ")]],
        resize_keyboard=True,
        one_time_keyboard=True
    )

    msg = await message.answer("Приоритет?", reply_markup=kb)
    await state.update_data(last_bot_message=msg.message_id)


@dp.message(ArtistForm.priority)
async def process_priority(message: Message, state: FSMContext):
    data = await state.get_data()
    await clean_prev_message(message, data, state)

    await state.update_data(priority=message.text)
    await state.set_state(ArtistForm.comment)
    msg = await message.answer("Комментарий? (или напиши 'нет')")
    await state.update_data(last_bot_message=msg.message_id)


@dp.message(ArtistForm.comment)
async def process_comment(message: Message, state: FSMContext):
    data = await state.get_data()
    await clean_prev_message(message, data, state)

    comment = message.text if message.text.lower() != "нет" else ""
    date_added = datetime.now().strftime("%d.%m.%Y")

    row = [
        str(message.from_user.id),  # добавляем user_id
        data['name'], data['telegram'], data['instagram'], data['phone'], data['email'],
        data['style'], data['level'], data['priority'], "", "", "", comment, date_added, ""
    ]

    try:
        sheet.append_row(row)
        await message.answer(
            f"✅ Артист добавлен!\n\n"
            f"🎤 Имя: {data['name']}\n"
            f"📱 Телега: {data['telegram']}\n"
            f"📸 Инста: {data['instagram']}\n"
            f"📞 Телефон: {data['phone']}\n"
            f"📧 Почта: {data['email']}\n"
            f"🎵 Стиль: {data['style']}\n"
            f"🏆 Уровень: {data['level']}\n"
            f"🔥 Приоритет: {data['priority']}\n"
            f"📝 Комментарий: {comment}\n"
            f"📅 Добавлено: {date_added}"
        )
    except Exception as e:
        await message.answer(f"❌ Ошибка при добавлении: {e}")

    await state.clear()
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

@dp.message(Command("list"))
async def list_with_buttons(message: Message, state: FSMContext):
    await clean_chat(message, state)

    try:
        args = message.text.split()
        if len(args) < 2:
            await message.answer("❌ Укажи стиль. Например: /list Yeat")
            return

        style = args[1].strip().lower()
        user_id = str(message.from_user.id)

        records = sheet.get_all_values()
        found = False

        for row in records[1:]:
            if row[0] == user_id and row[6].strip().lower() == style:
                found = True

                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="📄 Карточка", callback_data=f"card_{row[1]}")],
                    [InlineKeyboardButton(text="✏️ Редактировать", callback_data=f"edit_{row[1]}")],
                    [InlineKeyboardButton(text="📤 Отправить биты", callback_data=f"send_{row[1]}")]
                ])

                await message.answer(f"🎤 {row[1]} (@{row[2]}) — {row[7]}", reply_markup=keyboard)

        if not found:
            await message.answer(f"❌ У тебя нет артистов в стиле '{style}'.")

    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")

ADMIN_ID = "631172327"  # <-- сюда вставь свой Telegram ID (можешь узнать написав /id в любом боте)

@dp.message(Command("alllist"))
async def all_list(message: Message, state: FSMContext):
    await clean_chat(message, state)

    try:
        if str(message.from_user.id) != ADMIN_ID:
            await message.answer("❌ У тебя нет доступа к этой команде.")
            return

        records = sheet.get_all_values()
        result = []

        for row in records[1:]:
            result.append(f"👤 {row[1]} (@{row[2]}) — {row[7]} | 👨‍💻 ID: {row[0]}")

        if result:
            await message.answer("\n".join(result))
        else:
            await message.answer("❌ База пуста.")

    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")


@dp.message(Command("artist"))
async def show_artist(message: Message, state: FSMContext):
    await clean_chat(message, state)

    try:
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            await message.answer("❌ Укажи имя артиста. Например: /artist OG Buda")
            return

        name = args[1].strip().lower()
        user_id = str(message.from_user.id)

        records = sheet.get_all_values()
        for row in records[1:]:
            if row[0] == user_id and row[1].strip().lower() == name:
                await message.answer(
                    f"🎤 Имя: {row[1]}\n"
                    f"📱 Телега: {row[2]}\n"
                    f"📸 Инста: {row[3]}\n"
                    f"📞 Телефон: {row[4]}\n"
                    f"📧 Почта: {row[5]}\n"
                    f"🎵 Стиль: {row[6]}\n"
                    f"🏆 Уровень: {row[7]}\n"
                    f"🔥 Приоритет: {row[8]}\n"
                    f"📤 Последняя отправка: {row[9]}\n"
                    f"🎼 Какие биты: {row[10]}\n"
                    f"💬 Реакция: {row[11]}\n"
                    f"📝 Комментарий: {row[12]}\n"
                    f"📅 Добавлено: {row[13]}\n"
                    f"📅 Последний контакт: {row[14]}"
                )
                return

        await message.answer(f"❌ Артист с именем '{name}' не найден в твоей базе.")

    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")



@dp.message(Command("send"))
async def start_send_beats(message: Message, state: FSMContext):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("❌ Укажи имя артиста. Например: /send OG Buda")
        return

    name = args[1].strip()

    await state.update_data(name=name)
    await state.set_state(SendBitoForm.beats)
    await message.answer(f"🎼 Какие биты отправил {name}? (введи названия)")


@dp.message(SendBitoForm.beats)
async def process_beats(message: Message, state: FSMContext):
    await state.update_data(beats=message.text)
    await state.set_state(SendBitoForm.reaction)
    await message.answer("💬 Какая реакция? (что ответил артист?)")


@dp.message(SendBitoForm.reaction)
async def process_reaction(message: Message, state: FSMContext):
    data = await state.get_data()
    await clean_prev_message(message, data, state)

    name = data['name']
    beats = data['beats']
    reaction = message.text
    user_id = str(message.from_user.id)

    date_now = datetime.now().strftime("%d.%m.%Y")

    records = sheet.get_all_values()

    for i, row in enumerate(records[1:], start=2):
        if row[0] == user_id and row[1].strip().lower() == name.strip().lower():
            sheet.update(f"I{i}", [[date_now]])  # Последняя отправка
            sheet.update(f"J{i}", [[beats]])     # Какие биты
            sheet.update(f"K{i}", [[reaction]]) # Реакция
            sheet.update(f"N{i}", [[date_now]]) # Последний контакт
            await message.answer(f"✅ Отправка зафиксирована для {row[1]}\n📤 Последняя отправка: {date_now}\n🎼 Биты: {beats}\n💬 Реакция: {reaction}")
            await state.clear()
            return

    await message.answer(f"❌ Ошибка, артист '{name}' не найден.")
    await state.clear()

@dp.message(Command("remind"))
async def remind_contacts(message: Message):
    try:
        records = sheet.get_all_values()
        now = datetime.now()
        result = []

        for row in records[1:]:
            last_contact = row[13].strip()
            if last_contact:
                last_contact_date = datetime.strptime(last_contact, "%d.%m.%Y")
                if now - last_contact_date > timedelta(days=30):
                    result.append(f"🎤 {row[0]} — последний контакт: {last_contact}")

        if result:
            await message.answer("🔔 Артисты, с кем давно не общался:\n" + "\n".join(result))
        else:
            await message.answer("✅ Все контакты свежие!")

    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")

@dp.message(Command("help"))
async def help_command(message: Message):
    await message.answer(
        await message.answer("Команды:\n"
                         "/add - Добавить артиста\n"
                         "/mylist - Мои артисты\n"
                         "/search [запрос] - Поиск\n"
                         "/stats - Статистика\n"
                         "/top /potential /cold - Фильтры по приоритетам\n"
                         "/artist [имя] - Карточка артиста\n"
                         "/send [имя] - Фиксация отправки\n"
                         "/deal [имя сумма] - Фиксация сделки\n"
                         "/remindme [имя] - Ждёт напоминание\n"
                         "/export - Выгрузка базы\n"
                         "/score - Баллы активности\n"
                         "/contact [имя] - Обновить контакт\n"
                         "/checkpoint [имя этап] - Этапы\n"
                         "/edit [имя поле значение] - Редактировать")
    )

@dp.message(Command("edit"))
async def edit_artist(message: Message):
    try:
        args = message.text.split(maxsplit=3)
        if len(args) < 4:
            await message.answer("❌ Неверный формат. Пример:\n/edit OG Buda почта ivan@gmail.com")
            return

        name = args[1].strip().lower()
        field = args[2].strip().lower()
        new_value = args[3].strip()
        user_id = str(message.from_user.id)

        field_map = {
            'почта': 5,
            'телефон': 4,
            'телега': 2,
            'инста': 3,
            'стиль': 6,
            'уровень': 7,
            'приоритет': 8,
            'комментарий': 12
        }

        if field not in field_map:
            await message.answer("❌ Поле не найдено. Доступные поля: почта, телефон, телега, инста, стиль, уровень, приоритет, комментарий")
            return

        column_index = field_map[field]
        records = sheet.get_all_values()

        for i, row in enumerate(records[1:], start=2):
            if row[0] == user_id and row[1].strip().lower() == name:
                sheet.update_cell(i, column_index + 1, new_value)  # +1, так как индексация с 1
                await message.answer(f"✅ Поле '{field}' артиста '{row[1]}' обновлено: {new_value}")
                return

        await message.answer(f"❌ Артист '{name}' не найден в твоей базе.")

    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")
@dp.message(Command("mylist"))
async def mylist(message: Message, state: FSMContext):
    await clean_chat(message, state)
    user_id = str(message.from_user.id)
    records = sheet.get_all_values()
    result = [f"🎤 {row[1]} (@{row[2]}) — {row[7]}" for row in records[1:] if row[0] == user_id]

    await message.answer("\n".join(result) if result else "❌ У тебя нет артистов.")

@dp.message(Command("export"))
async def export_database(message: Message, state: FSMContext):
    await clean_chat(message, state)

    try:
        records = sheet.get_all_values()

        # Создаем CSV в памяти
        output = StringIO()
        writer = csv.writer(output)

        # Записываем все строки из Google Таблицы
        for row in records:
            writer.writerow(row)

        output.seek(0)

        # Отправляем файл пользователю
        await message.answer_document(
            document=types.BufferedInputFile(
                output.getvalue().encode(),
                filename=f"artists_base_{datetime.now().strftime('%d_%m_%Y')}.csv"
            ),
            caption="📄 Ваша база артистов"
        )

    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")


@dp.message(Command("remindme"))
async def set_reminder(message: Message, state: FSMContext):
    await clean_chat(message, state)

    try:
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            await message.answer("❌ Укажи имя артиста. Например: /remindme OG Buda")
            return

        name = args[1].strip().lower()
        user_id = str(message.from_user.id)
        records = sheet.get_all_values()

        for i, row in enumerate(records[1:], start=2):
            if row[0] == user_id and row[1].strip().lower() == name:
                sheet.update(f"O{i}", [["Да"]])  # Колонка Ждёт напоминание
                await message.answer(f"✅ Артисту {row[1]} установлен статус 'Ждёт напоминание'")
                return

        await message.answer(f"❌ Артист '{name}' не найден.")

    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")


@dp.message(Command("deal"))
async def set_deal(message: Message, state: FSMContext):
    await clean_chat(message, state)

    try:
        args = message.text.split(maxsplit=2)
        if len(args) < 3:
            await message.answer("❌ Укажи имя артиста и сумму. Например: /deal OG Buda 3000")
            return

        name = args[1].strip().lower()
        amount = args[2].strip()
        user_id = str(message.from_user.id)
        date_now = datetime.now().strftime("%d.%m.%Y")

        records = sheet.get_all_values()

        for i, row in enumerate(records[1:], start=2):
            if row[0] == user_id and row[1].strip().lower() == name:
                sheet.update(f"P{i}", [[amount]])  # Колонка Сделка
                sheet.update(f"N{i}", [[date_now]])  # Последний контакт
                await message.answer(f"✅ Сделка на сумму {amount}₽ зафиксирована для {row[1]}")
                return

        await message.answer(f"❌ Артист '{name}' не найден.")

    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")

@dp.message(Command("contact"))
async def update_contact(message: Message, state: FSMContext):
    await clean_chat(message, state)

    try:
        args = message.text.split(maxsplit=1)
        if len(args) < 2:
            await message.answer("❌ Укажи имя артиста. Например: /contact OG Buda")
            return

        name = args[1].strip().lower()
        user_id = str(message.from_user.id)
        date_now = datetime.now().strftime("%d.%m.%Y")

        records = sheet.get_all_values()

        for i, row in enumerate(records[1:], start=2):
            if row[0] == user_id and row[1].strip().lower() == name:
                sheet.update(f"N{i}", [[date_now]])
                await message.answer(f"✅ Последний контакт с {row[1]} обновлён на {date_now}")
                return

        await message.answer(f"❌ Артист '{name}' не найден.")

    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")


@dp.message(Command("score"))
async def score(message: Message, state: FSMContext):
    await clean_chat(message, state)

    try:
        user_id = str(message.from_user.id)
        records = sheet.get_all_values()

        add_count = 0
        send_count = 0
        deal_count = 0

        for row in records[1:]:
            if row[0] == user_id:
                if row[1]:  # Имя артиста
                    add_count += 1
                if row[9]:  # Последняя отправка
                    send_count += 1
                if row[15]:  # Сделка
                    deal_count += 1

        score = (add_count * 1) + (send_count * 3) + (deal_count * 10)

        await message.answer(f"📊 Твой счёт активности:\n"
                             f"Добавлено артистов: {add_count}\n"
                             f"Отправок битов: {send_count}\n"
                             f"Закрыто сделок: {deal_count}\n\n"
                             f"Общий счёт: {score} баллов")

    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")



@dp.message(Command("checkpoint"))
async def set_checkpoint(message: Message, state: FSMContext):
    await clean_chat(message, state)

    try:
        args = message.text.split(maxsplit=2)
        if len(args) < 3:
            await message.answer("❌ Укажи имя артиста и этап (1-4). Например: /checkpoint OG Buda 2")
            return

        name = args[1].strip().lower()
        stage = args[2].strip()
        user_id = str(message.from_user.id)

        records = sheet.get_all_values()

        for i, row in enumerate(records[1:], start=2):
            if row[0] == user_id and row[1].strip().lower() == name:
                sheet.update(f"Q{i}", [[stage]])
                await message.answer(f"✅ Установлен этап {stage} для {row[1]}")
                return

        await message.answer(f"❌ Артист '{name}' не найден.")

    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")




@dp.message(Command("stats"))
async def stats(message: Message, state: FSMContext):
    await clean_chat(message, state)
    user_id = str(message.from_user.id)
    records = sheet.get_all_values()

    total, top, potential, cold = 0, 0, 0, 0
    for row in records[1:]:
        if row[0] == user_id:
            total += 1
            if row[8] == "🔥 ТОП":
                top += 1
            elif row[8] == "💸 ПОТЕНЦИАЛ":
                potential += 1
            elif row[8] == "❄️ ХОЛОДНЫЙ":
                cold += 1

    await message.answer(f"📊 Всего: {total}\n🔥 ТОП: {top}\n💸 Потенциал: {potential}\n❄️ Холодные: {cold}")


async def filter_by_priority(message, state, priority):
    await clean_chat(message, state)
    user_id = str(message.from_user.id)
    records = sheet.get_all_values()
    result = [f"🎤 {row[1]} (@{row[2]}) — {row[7]}" for row in records[1:] if row[0] == user_id and row[8] == priority]

    await message.answer("\n".join(result) if result else f"❌ У тебя нет артистов с приоритетом {priority}")


@dp.message(Command("top"))
async def top(message: Message, state: FSMContext):
    await filter_by_priority(message, state, "🔥 ТОП")


@dp.message(Command("potential"))
async def potential(message: Message, state: FSMContext):
    await filter_by_priority(message, state, "💸 ПОТЕНЦИАЛ")


@dp.message(Command("cold"))
async def cold(message: Message, state: FSMContext):
    await filter_by_priority(message, state, "❄️ ХОЛОДНЫЙ")


@dp.message(Command("artist"))
async def artist(message: Message, state: FSMContext):
    await clean_chat(message, state)
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("❌ Укажи имя артиста.")
        return

    user_id = str(message.from_user.id)
    name = args[1].strip().lower()
    records = sheet.get_all_values()

    for row in records[1:]:
        if row[0] == user_id and row[1].strip().lower() == name:
            await message.answer(
                f"🎤 Имя: {row[1]}\n"
                f"📱 Телега: <a href='https://t.me/{row[2][1:]}'>{row[2]}</a>\n"
                f"📸 Инста: <a href='https://instagram.com/{row[3][1:]}'>{row[3]}</a>\n"
                f"📞 Телефон: {row[4]}\n"
                f"📧 Почта: {row[5]}\n"
                f"🎵 Стиль: {row[6]}\n"
                f"🏆 Уровень: {row[7]}\n"
                f"🔥 Приоритет: {row[8]}\n",
                parse_mode=ParseMode.HTML)
            return

    await message.answer("❌ Артист не найден.")


async def reminder_task():
    while True:
        await asyncio.sleep(60 * 60 * 24)
        try:
            now = datetime.now()
            records = sheet.get_all_values()
            for row in records[1:]:
                last_contact = row[14].strip()
                if last_contact:
                    date = datetime.strptime(last_contact, "%d.%m.%Y")
                    if (now - date).days > 30:
                        await bot.send_message(row[0], f"⚠️ Ты давно не писал {row[1]} (с {last_contact})")
        except Exception as e:
            print(f"Ремайндер ошибка: {e}")

@dp.callback_query(lambda c: c.data.startswith('card_'))
async def card_callback(callback: types.CallbackQuery):
    name = callback.data.split("_")[1]
    await callback.message.answer(f"/artist {name}")
    await callback.answer()


@dp.callback_query(lambda c: c.data.startswith('edit_'))
async def edit_callback(callback: types.CallbackQuery):
    name = callback.data.split("_")[1]
    await callback.message.answer(f"/edit {name} [поле] [новое значение]")
    await callback.answer()


@dp.callback_query(lambda c: c.data.startswith('send_'))
async def send_callback(callback: types.CallbackQuery):
    name = callback.data.split("_")[1]
    await callback.message.answer(f"/send {name}")
    await callback.answer()


async def on_startup():
    global sheet
    sheet = client.open_by_key("1AFQY1SYlsczjEnBOLS6390qhEsKHVBMiqBMwdUyVaAI").sheet1
    print("✅ Бот запущен и подключен к Google Таблице!")

if __name__ == "__main__":
    import asyncio
    asyncio.run(on_startup())
    asyncio.run(dp.start_polling(bot))

