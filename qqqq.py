import logging
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardRemove,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)
from telegram.request import HTTPXRequest

# ====== НАСТРОЙКИ ======
TOKEN = "8937941894:AAFepAiQiydPxkUKGU8G_PRb1p9wZ0Ef0ao"
ADMIN_CHAT_ID = 8837425135

logging.basicConfig(level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)

# Состояния диалога
CHOOSING, MODEL_FORM, MODEL_PHOTO_FACE, MODEL_PHOTO_FULL, OPERATOR_FORM = range(5)


# ================= СТАРТ / МЕНЮ =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📋 Анкета для моделей", callback_data="choose_model")],
        [InlineKeyboardButton("🖥 Анкета для операторов", callback_data="choose_operator")],
    ])
    await update.message.reply_text(
        "Привет! Выбери, какую анкету хочешь заполнить:",
        reply_markup=keyboard,
    )
    return CHOOSING


# ================= ВЫБОР: АНКЕТА ДЛЯ МОДЕЛЕЙ =================
async def choose_model(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    form_text = (
        "Анкета для моделей\n"
        "• Имя\n"
        "• город\n"
        "• Номер телефона\n"
        "• Дата рождения\n"
        "• Знания английского от 0 до 10\n"
        "• Проживание: одна/не одна\n"
        "• Есть 2 мобильных телефона или комп + телефон?\n"
        "• Модель устройства\n"
        "• Сколько часов и дней в неделю готова уделять работе?\n"
        "• Есть наушники?\n"
        "• Телеграм для связи\n\n"
        "Заполни анкету и отправь ОДНИМ сообщением 👇"
    )
    await query.edit_message_text(form_text)
    return MODEL_FORM


async def get_model_form(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["form_text"] = update.message.text
    await update.message.reply_text("Отлично! Теперь отправь фото в анфас 📸")
    return MODEL_PHOTO_FACE


async def get_model_photo_face(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.photo:
        await update.message.reply_text("Пожалуйста, отправь именно фото.")
        return MODEL_PHOTO_FACE
    context.user_data["photo_face"] = update.message.photo[-1].file_id
    await update.message.reply_text("Отлично! Теперь фото в полный рост 📸")
    return MODEL_PHOTO_FULL


async def get_model_photo_full(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.photo:
        await update.message.reply_text("Пожалуйста, отправь именно фото.")
        return MODEL_PHOTO_FULL
    context.user_data["photo_full"] = update.message.photo[-1].file_id

    user = update.effective_user
    summary = (
        f"🆕 Новая анкета (МОДЕЛЬ)\n"
        f"От: @{user.username if user.username else user.first_name}\n\n"
        f"{context.user_data['form_text']}"
    )

    await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=summary)
    await context.bot.send_photo(
        chat_id=ADMIN_CHAT_ID,
        photo=context.user_data["photo_face"],
        caption="Фото: анфас",
    )
    await context.bot.send_photo(
        chat_id=ADMIN_CHAT_ID,
        photo=context.user_data["photo_full"],
        caption="Фото: полный рост",
    )

    await update.message.reply_text(
        "Спасибо! Твоя анкета отправлена ✅\nС тобой свяжутся в ближайшее время."
    )
    return ConversationHandler.END


# ================= ВЫБОР: АНКЕТА ДЛЯ ОПЕРАТОРОВ =================
async def choose_operator(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    form_text = (
        "Анкета для операторов\n"
        "—Анкета—\n"
        "1. Имя и фамилия:\n"
        "2. Дата рождения:\n"
        "3. Видеокарта:\n"
        "4. Процессор:\n"
        "5. Оперативка и ее частота:\n"
        "6. Скорость интернет-соединения (мбит/сек | mbps):\n"
        "7. Уровень знания английского:\n"
        "8. Номер телефона:\n"
        "9. Username в тг:\n"
        "10. Опыт в адулте:\n\n"
        "Заполни анкету и отправь ОДНИМ сообщением 👇"
    )
    await query.edit_message_text(form_text)
    return OPERATOR_FORM


async def get_operator_form(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    summary = (
        f"🆕 Новая анкета (ОПЕРАТОР)\n"
        f"От: @{user.username if user.username else user.first_name}\n\n"
        f"{update.message.text}"
    )

    await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=summary)

    await update.message.reply_text(
        "Спасибо! Твоя анкета отправлена ✅\nС тобой свяжутся в ближайшее время."
    )
    return ConversationHandler.END


# ================= ОТМЕНА =================
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Анкета отменена. Чтобы начать заново, напиши /start",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END


def main():
    request = HTTPXRequest(
        connect_timeout=30,
        read_timeout=30,
        write_timeout=30,
        pool_timeout=30,
    )

    app = Application.builder().token(TOKEN).request(request).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING: [
                CallbackQueryHandler(choose_model, pattern="^choose_model$"),
                CallbackQueryHandler(choose_operator, pattern="^choose_operator$"),
            ],
            MODEL_FORM: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_model_form)],
            MODEL_PHOTO_FACE: [MessageHandler(filters.PHOTO, get_model_photo_face)],
            MODEL_PHOTO_FULL: [MessageHandler(filters.PHOTO, get_model_photo_full)],
            OPERATOR_FORM: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_operator_form)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    print("Бот запущен и работает...")
    app.run_polling()


if __name__ == "__main__":
    main()