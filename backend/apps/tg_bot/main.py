import logging
import os

from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TARGET_CHAT_ID = os.getenv("TARGET_CHAT_ID")


async def send_to_target_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if str(chat_id) == TARGET_CHAT_ID:
        await context.bot.send_message(chat_id=chat_id, text=update.message.text)


def kek():
    from apps.orders.models import Order

    print(Order.objects.first())


if __name__ == '__main__':
    pass
    # application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    #
    # send_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), send_to_target_chat)
    # application.add_handler(send_handler)
    # application.run_polling()

    kek()
