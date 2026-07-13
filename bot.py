from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

from flask import Flask
from threading import Thread
import os


TOKEN = "мой токен"
ADMIN_ID = 8502272769

NAME, PHONE, ORDER = range(3)


# ===== Render Web Server =====

web_app = Flask(__name__)

@web_app.route("/")
def home():
    return "Zohidovs Parfum Bot is running!"

def run_web():
    web_app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
    )

Thread(target=run_web).start()


# ===== Telegram Bot =====

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["🛍 Каталог", "📦 Заказать"],
        ["📞 Связаться"]
    ]

    await update.message.reply_text(
        "🖤 Добро пожаловать в Zohidovs Parfum!",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )


async def order_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Напишите ваше имя:")
    return NAME


async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("Теперь напишите номер телефона:")
    return PHONE


async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["phone"] = update.message.text
    await update.message.reply_text("Какой аромат хотите заказать?")
    return ORDER


async def get_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    perfume = update.message.text

    name = context.user_data["name"]
    phone = context.user_data["phone"]

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=(
            "🛒 Новый заказ!\n\n"
            f"Имя: {name}\n"
            f"Телефон: {phone}\n"
            f"Аромат: {perfume}"
        )
    )

    await update.message.reply_text(
        "✅ Спасибо за заказ!\n\n"
        f"Имя: {name}\n"
        f"Телефон: {phone}\n"
        f"Аромат: {perfume}\n\n"
        "Мы скоро свяжемся с вами."
    )

    return ConversationHandler.END


async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "🛍 Каталог":
        await update.message.reply_text(
            "✨ Каталог скоро будет добавлен."
        )

    elif text == "📞 Связаться":
        await update.message.reply_text(
            "📩 Свяжитесь с нами: @Azimmmm6"
        )


app = Application.builder().token(TOKEN).build()


conv = ConversationHandler(
    entry_points=[
        MessageHandler(filters.Regex("📦 Заказать"), order_start)
    ],
    states={
        NAME: [MessageHandler(filters.TEXT, get_name)],
        PHONE: [MessageHandler(filters.TEXT, get_phone)],
        ORDER: [MessageHandler(filters.TEXT, get_order)],
    },
    fallbacks=[]
)


app.add_handler(CommandHandler("start", start))
app.add_handler(conv)
app.add_handler(MessageHandler(filters.TEXT, buttons))


print("Бот запущен!")
app.run_polling()
