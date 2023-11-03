import os
from functools import wraps

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from .main import TARGET_CHAT_ID, BOT

app = FastAPI()

API_NAME = os.getenv("API_NAME")
API_KEY = os.getenv("API_KEY")


def access_verification(view_func):
    """Декоратор проверки доступа. Проверяет доступен ли ключ доступа и его значение"""

    @wraps(view_func)
    def _wrapped_view(data):
        if API_NAME not in data or data[API_NAME] != API_KEY:
            return JSONResponse({"error": "Access denied"})

        return view_func(data)

    return _wrapped_view


@app.post("/notification/send_error/")
@access_verification
def send_error(data: dict):
    """Отправка ошибок в закрытую группу ТГ"""

    BOT.send_message(TARGET_CHAT_ID, data["message"])
    return JSONResponse({"success": True})


@app.post("/notification/send_message/")
@access_verification
def send_message(data: dict):
    """Отправка успешных сообщений в закрытую группу ТГ"""

    BOT.send_message(TARGET_CHAT_ID, data["message"])
    return JSONResponse({"success": True})
