from typing import Final

from telegram import (
    Update,
    Bot,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN: Final = "8354724654:AAG0GbhA-9CO29OOrwBrS2zzRYpAAljo73w"
BOT_USERNAME: Final = "@mattuuniversitystudentsquote_bot"
ADMIN_ID: Final = 6971559533

NAME, QUOTE, PHOTO, CONSENT = range(4)


# ---------------- COMMANDS ----------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to *Peace Forum*\n\n"
        "Send your quote and photo to be featured.\n\n"
        "First, what is your name or nickname?",
        parse_mode="Markdown",
    )
    return NAME


async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("✍️ Please send your quote:")
    return QUOTE


async def get_quote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["quote"] = update.message.text
    await update.message.reply_text(
        "📸 Now send your photo (clear portrait preferred):"
    )
    return PHOTO


async def get_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    context.user_data["photo"] = photo.file_id

    keyboard = [["Yes, I agree"], ["No, cancel"]]

    await update.message.reply_text(
        "✅ Do you agree to have your quote and photo posted on *Peace Forum*?",
        reply_markup=ReplyKeyboardMarkup(
            keyboard,
            one_time_keyboard=True,
            resize_keyboard=True,
        ),
        parse_mode="Markdown",
    )
    return CONSENT


async def get_consent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text.lower().startswith("yes"):
        await send_to_admin(update, context)
        await update.message.reply_text(
            "🙏 Thank you! Your submission has been received.\n"
            "If approved, it will be posted soon.",
            reply_markup=ReplyKeyboardRemove(),
        )
    else:
        await update.message.reply_text(
            "❌ Submission canceled.",
            reply_markup=ReplyKeyboardRemove(),
        )

    context.user_data.clear()
    return ConversationHandler.END


async def send_to_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🕊 *New Peace Forum Submission*\n\n"
        f"👤 *Name:* {context.user_data['name']}\n\n"
        f"💬 *Quote:*\n{context.user_data['quote']}"
    )

    await context.bot.send_photo(
        chat_id=ADMIN_ID,
        photo=context.user_data["photo"],
        caption=text,
        parse_mode="Markdown",
    )


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Submission canceled.")
    context.user_data.clear()
    return ConversationHandler.END


# ---------------- MAIN ----------------

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            QUOTE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_quote)],
            PHOTO: [MessageHandler(filters.PHOTO, get_photo)],
            CONSENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_consent)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv)

    print("🤖 Peace Forum Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()