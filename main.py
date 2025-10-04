import os
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# Получаем токен и ID из переменных окружения Railway
TOKEN = os.getenv("BOT_TOKEN")  # обязательно создайте переменную BOT_TOKEN в Railway
ADMIN_ID = int(os.getenv("ADMIN_ID"))  # создайте переменную ADMIN_ID в Railway

# Словарь для связи сообщений админа и пользователей
message_map = {}

# 📩 Обработка сообщений от пользователей
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == ADMIN_ID:
        return  # игнорируем сообщения самого админа

    user_id = update.message.from_user.id
    username = update.message.from_user.username or "Без ника"
    first_name = update.message.from_user.first_name or "Без имени"

    # --- 1. Ответ пользователю (анонимный) ---
    await update.message.reply_text("✅ Твоё анонимное сообщение получено!")

    # --- 2. Отправка админу ---
    header = (
        f"👤 Новое сообщение:\n"
        f"ID: {user_id}\n"
        f"Имя: {first_name}\n"
        f"Юзернейм: @{username}"
    )

    # Сначала текст (если есть)
    if update.message.text:
        admin_msg = await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"{header}\n\n📩 Текст: {update.message.text}"
        )
    else:
        admin_msg = await context.bot.send_message(chat_id=ADMIN_ID, text=header)

    # Сохраняем связь для ответа
    message_map[admin_msg.message_id] = user_id

    # Пересылаем вложения
    if update.message.photo:
        await context.bot.send_photo(ADMIN_ID, update.message.photo[-1].file_id, caption="📷 Фото")
    if update.message.document:
        await context.bot.send_document(ADMIN_ID, update.message.document.file_id, caption="📄 Документ")
    if update.message.voice:
        await context.bot.send_voice(ADMIN_ID, update.message.voice.file_id, caption="🎤 Голосовое")
    if update.message.audio:
        await context.bot.send_audio(ADMIN_ID, update.message.audio.file_id, caption="🎵 Аудио")
    if update.message.video:
        await context.bot.send_video(ADMIN_ID, update.message.video.file_id, caption="🎬 Видео")
    if update.message.sticker:
        await context.bot.send_sticker(ADMIN_ID, update.message.sticker.file_id)

# 🔄 Обработка ответов админа
async def handle_admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    if update.message.reply_to_message:
        reply_to_id = update.message.reply_to_message.message_id
        if reply_to_id in message_map:
            user_id = message_map[reply_to_id]

            # Отправка текста
            if update.message.text:
                await context.bot.send_message(chat_id=user_id, text=f"📩 Ответ от админа:\n{update.message.text}")

            # Отправка вложений
            if update.message.photo:
                await context.bot.send_photo(user_id, update.message.photo[-1].file_id)
            if update.message.document:
                await context.bot.send_document(user_id, update.message.document.file_id)
            if update.message.voice:
                await context.bot.send_voice(user_id, update.message.voice.file_id)
            if update.message.audio:
                await context.bot.send_audio(user_id, update.message.audio.file_id)
            if update.message.video:
                await context.bot.send_video(user_id, update.message.video.file_id)
            if update.message.sticker:
                await context.bot.send_sticker(user_id, update.message.sticker.file_id)

            await update.message.reply_text("✅ Ответ отправлен пользователю.")
        else:
            await update.message.reply_text("⚠ Пользователь не найден.")

def main():
    app = Application.builder().token(TOKEN).build()

    # Ловим все сообщения от пользователей
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_message))

    # Ловим ответы админа
    app.add_handler(MessageHandler(filters.ALL & filters.REPLY, handle_admin_reply))

    app.run_polling()

if __name__ == "__main__":
    main()

