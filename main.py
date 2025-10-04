import os
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# берем токен и id из Railway Variables
TOKEN = os.getenv("8228754936:AAG6zuPPPBxG5Ljc5MHazuCb3AhiSdTtc84")
ADMIN_ID = int(os.getenv("7714575966"))

# проверка, что переменные существуют
if not TOKEN or not ADMIN_ID:
    raise ValueError("❌ Переменные окружения TOKEN и ADMIN_ID не заданы на Railway!")

# связь сообщений
message_map = {}


# 📩 обработка входящих сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == ADMIN_ID:
        return  # игнорируем твои сообщения как пользователя

    user_id = update.message.from_user.id
    username = update.message.from_user.username or "Без ника"
    first_name = update.message.from_user.first_name or "Без имени"

    # ответ пользователю
    await update.message.reply_text("✅ Твоё анонимное сообщение получено!")

    # сообщение админу
    header = (
        f"👤 Новое сообщение:\n"
        f"ID: {user_id}\n"
        f"Имя: {first_name}\n"
        f"Юзернейм: @{username}"
    )

    admin_msg = await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"{header}\n\n📩 Текст: {update.message.text}" if update.message.text else header
    )

    message_map[admin_msg.message_id] = user_id


# 🔄 обработка ответов админа
async def handle_admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    if update.message.reply_to_message:
        reply_to_id = update.message.reply_to_message.message_id
        if reply_to_id in message_map:
            user_id = message_map[reply_to_id]

            if update.message.text:
                await context.bot.send_message(chat_id=user_id, text=f"📩 Ответ от админа:\n{update.message.text}")

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

    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.ALL & filters.REPLY, handle_admin_reply))

    print("🤖 Бот запущен и работает на Railway!")
    app.run_polling()


if _name_ == "_main_":
    main()

