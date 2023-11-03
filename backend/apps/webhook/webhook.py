import json
import os
from functools import wraps

from apps.tgbot.main import BOT
from apps.utils import MessageSender
from apps.webhook.manager import DataManager
from apps.webhook.serializers import WebhookSerializer
from django.http import JsonResponse, HttpResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from sentry_sdk import capture_exception

API_NAME = os.getenv("API_NAME")
API_KEY = os.getenv("API_KEY")


def access_verification(view_func):
    """Декоратор проверки доступа. Проверяет доступен ли ключ доступа и его значение"""

    @wraps(view_func)
    def _wrapped_view(self, request, *args, **kwargs):
        try:
            if 'message' in request.POST or 'update_id' in request.POST:
                data = request.body.decode('UTF-8')
                return view_func(self, request, data, *args, **kwargs)

            data = json.loads(request.body.decode("unicode_escape"))
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"})

        if API_NAME not in data or data[API_NAME] != API_KEY:
            return JsonResponse({'error': "Access denied"})

        return view_func(self, request, data, *args, **kwargs)

    return _wrapped_view


@method_decorator(csrf_exempt, name="dispatch")
class WebhookView(View):
    """Вебхук, получающий данные от Tilda"""

    @access_verification
    def post(self, request, data, *args, **kwargs):

        if 'message' in request.POST or 'update_id' in request.POST:
            update = BOT.types.Update.de_json(data)
            BOT.process_new_updates([update])
            return HttpResponse(status=200)

        serializer = WebhookSerializer()
        try:
            customer, order, products = serializer.serialize(data)
        except Exception as e:
            capture_exception(e)
            MessageSender().send_error_message(f"Ошибка получения данных через webhook: {e}")
            return JsonResponse({"error": "Data serialization error"})

        manager = DataManager(customer, order, products)
        manager.save_data()
        return JsonResponse({})

