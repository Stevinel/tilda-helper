import os
import json

from functools import wraps

from sentry_sdk import capture_exception
from config.settings import logger

from apps.utils import MessageSender
from apps.orders.manager import DataManager
from apps.orders.serializers import WebhookSerializer

from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt


API_NAME = os.getenv('API_NAME')
API_KEY = os.getenv('API_KEY')
ALLOWED_CHATS = [x.strip() for x in os.getenv('ALLOWED_CHATS').split(',')]


def access_verification(view_func):
    """Декоратор проверки доступа. Проверяет доступен ли ключ доступа и его значение"""

    @wraps(view_func)
    def _wrapped_view(self, request, *args, **kwargs):
        try:
            logger.info('Получен запрос на вэбхук')
            data = json.loads(request.body.decode('unicode_escape'))
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'})

        if API_NAME not in data or data[API_NAME] != API_KEY:
            return JsonResponse({'error': 'Access denied'})

        return view_func(self, request, data, bot=False, *args, **kwargs)

    return _wrapped_view


@method_decorator(csrf_exempt, name='dispatch')
class WebhookView(View):
    """Вебхук, получающий данные от Tilda и телеграм сервера"""

    @access_verification
    def post(self, request, data, *args, **kwargs):
        serializer = WebhookSerializer()
        try:
            customer, order, products = serializer.serialize(data)
        except Exception as e:
            capture_exception(e)
            MessageSender().send_error_message(f'Ошибка получения данных через webhook: {e}')
            return JsonResponse({'error': 'Data serialization error'})

        manager = DataManager(customer, order, products)
        manager.save_data()
        return JsonResponse({})
