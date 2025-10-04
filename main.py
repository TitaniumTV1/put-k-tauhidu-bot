from flask import Flask, request
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# === Настройки ===
TOKEN = "8228754936:AAG6zuPPPBxG5Ljc5MHazuCb3AhiSdTtc84"
ADMIN_ID = 7714575966   

# === Flask-приложение ===
app = Flask(__name__)

# === Telegram Application ===
application = Application.builder().token(TOKEN).build()

# связь: id админского сообщения -> id пользователя
message_map = {}


# 📩 обработка входящих сообщений от пользователей
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == ADMIN_ID:
        return  # игнорируем твои собственные сообщения

    user_id = update.message.from_user.id
    username = update.message.from_user.username or "Без ника"
    first_name = update.message.from_user.first_name or "Без имени"

    # --- ответ пользователю ---
    await update.message.reply_text("✅ Твоё анонимное сообщение получено!")

    # --- отправка админу ---
    header = (
        f"👤 Новое сообщение:\n"
        f"ID: {user_id}\n"
        f"Имя: {first_name}\n"
        f"Юзернейм: @{username}"
    )

    if update.message.text:
        admin_msg = await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"{header}\n\n📩 Текст: {update.message.text}"
        )
    else:
        admin_msg = await context.bot.send_message(chat_id=ADMIN_ID, text=header)

    message_map[admin_msg.message_id] = user_id

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


# === Flask Webhook ===
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put_nowait(update)
    return "ok", 200


@app.route("/")
def home():
    return "Бот работает!", 200


# === Регистрация хендлеров ===
application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_message))
application.add_handler(MessageHandler(filters.ALL & filters.REPLY, handle_admin_reply))


if _name_ == "_main_":
    app.run(host="0.0.0.0", port=8080)

