import os

import telebot

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TARGET_CHAT_ID = os.getenv("TARGET_CHAT_ID")

bot = telebot.TeleBot(TELEGRAM_TOKEN)


def wake_up_msg():
    bot.send_message(TARGET_CHAT_ID, "Я запустилься")


if __name__ == "__main__":
    wake_up_msg()
    bot.infinity_polling()
