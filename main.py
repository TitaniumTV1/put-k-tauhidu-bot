import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

# 🔹 Включаем логирование
logging.basicConfig(level=logging.INFO)

# 🔹 Загружаем переменные окружения из Railway
BOT_TOKEN = os.getenv("8228754936:AAG6zuPPPBxG5Ljc5MHazuCb3AhiSdTtc84")
ADMIN_ID = int(os.getenv("7714575966"))

# 🔹 Проверка, что токен и админ заданы
if not BOT_TOKEN or not ADMIN_ID:
    raise ValueError("❌ Ошибка: переменные BOT_TOKEN и ADMIN_ID не заданы в Railway Variables!")

# 🔹 Создаём бота и диспетчер
bot = Bot(token="8228754936:AAG6zuPPPBxG5Ljc5MHazuCb3AhiSdTtc84")
dp = Dispatcher(bot)

# Словарь: id админского сообщения → id пользователя
message_map = {}


# 📌 Команда /start
@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        await message.reply("👋 Привет, Админ! Бот запущен ✅")
    else:
        await message.reply("Привет! Напиши сообщение, и админ его получит.")


# 📩 Пересылка сообщений от пользователей админу
@dp.message_handler(lambda m: m.from_user.id != ADMIN_ID)
async def handle_user_message(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username or "Без ника"
    first_name = message.from_user.first_name or "Без имени"

    header = (
        f"👤 Новое сообщение:\n"
        f"ID: {user_id}\n"
        f"Имя: {first_name}\n"
        f"Юзернейм: @{username}"
    )

    # Отправляем админу сообщение
    admin_msg = await bot.send_message(
        chat_id=7714575966,
        text=f"{header}\n\n📩 {message.text or '[Вложение]'}"
    )

    # Запоминаем связь "сообщение админа → id пользователя"
    message_map[admin_msg.message_id] = user_id

    # Пересылаем вложения
    if message.photo:
        await bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption="📷 Фото")
    if message.document:
        await bot.send_document(ADMIN_ID, message.document.file_id, caption="📄 Документ")
    if message.voice:
        await bot.send_voice(ADMIN_ID, message.voice.file_id, caption="🎤 Голосовое")
    if message.audio:
        await bot.send_audio(ADMIN_ID, message.audio.file_id, caption="🎵 Аудио")
    if message.video:
        await bot.send_video(ADMIN_ID, message.video.file_id, caption="🎬 Видео")
    if message.sticker:
        await bot.send_sticker(ADMIN_ID, message.sticker.file_id)

    # Подтверждение пользователю
    await message.reply("✅ Твоё сообщение передано админу!")


# 🔄 Ответы админа
@dp.message_handler(lambda m: m.from_user.id == ADMIN_ID, content_types=types.ContentTypes.ANY)
async def handle_admin_reply(message: types.Message):
    if message.reply_to_message:
        reply_to_id = message.reply_to_message.message_id
        if reply_to_id in message_map:
            user_id = message_map[reply_to_id]

            # Отправка текста
            if message.text:
                await bot.send_message(user_id, f"📩 Ответ от админа:\n{message.text}")

            # Отправка вложений
            if message.photo:
                await bot.send_photo(user_id, message.photo[-1].file_id)
            if message.document:
                await bot.send_document(user_id, message.document.file_id)
            if message.voice:
                await bot.send_voice(user_id, message.voice.file_id)
            if message.audio:
                await bot.send_audio(user_id, message.audio.file_id)
            if message.video:
                await bot.send_video(user_id, message.video.file_id)
            if message.sticker:
                await bot.send_sticker(user_id, message.sticker.file_id)

            await message.reply("✅ Ответ отправлен пользователю.")
        else:
            await message.reply("⚠ Пользователь не найден.")


# 🚀 Запуск бота
if _name_ == "_main_":
    executor.start_polling(dp, skip_updates=True)

