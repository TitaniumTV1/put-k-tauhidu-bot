import os
import sys
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

# Читаем переменные из окружения
TOKEN = os.getenv("TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

# Проверяем наличие переменных
if not TOKEN:
    print("❌ Ошибка: переменная TOKEN не найдена. Добавь её в Railway → Variables")
    sys.exit(1)

if not ADMIN_ID:
    print("❌ Ошибка: переменная ADMIN_ID не найдена. Добавь её в Railway → Variables")
    sys.exit(1)

try:
    ADMIN_ID = int(ADMIN_ID)
except ValueError:
    print("❌ Ошибка: ADMIN_ID должен быть числом")
    sys.exit(1)

# Создаём бота
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Команда /start
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer("✅ Привет, админ! Бот работает.")
    else:
        await message.answer("👋 Привет! Ты пользователь бота.")

# Ответ на все остальные сообщения
@dp.message_handler()
async def echo(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer(f"📩 Сообщение получено: {message.text}")
    else:
        await message.answer("Ваше сообщение принято!")

if _name_ == "_main_":
    print("🚀 Бот запущен...")
    executor.start_polling(dp, skip_updates=True)
